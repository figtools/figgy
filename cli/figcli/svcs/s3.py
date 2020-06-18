from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from threading import Lock
from typing import Tuple, List, Union

import boto3
from botocore.response import StreamingBody
from tqdm import tqdm

from figcli.utils.utils import *

log = logging.getLogger(__name__)


@dataclass(repr=True)
class S3MatchResult:
    def __init__(self, s3_key: str,
                 matched_text: Union[str, None],
                 matched_context: Union[str, None],
                 skipped: bool = False):
        self.s3_key = s3_key
        self.matched_text = matched_text
        self._matched_context = matched_context
        self.skipped = skipped

    @property
    def matched_context(self):
        return self._matched_context

    @matched_context.setter
    def matched_context(self, text: str):
        self._matched_context = text if text else "N/A"

    def has_match(self) -> bool:
        return self.matched_text is not None

    def __hash__(self):
        return hash(self.s3_key)

    def __eq__(self, o):
        if isinstance(o, S3MatchResult):
            return o.s3_key == self.s3_key


class S3Service:
    _MAX_POOL_SIZE = 300
    """
    Provides functionality around S3
    """
    _SEARCHABLE_CONTENT_TYPES = ['application/json', 'application/xml', 'text/html', 'text/css', 'text/javascript',
                                 'text/csv']
    _SEARCHABLE_SUFFIXES = ['.json', '.txt', '.csv', '.xml', '.log']

    def __init__(self, env_session: boto3.Session):
        self._s3 = env_session.client('s3', config=botocore.client.Config(max_pool_connections=S3Service._MAX_POOL_SIZE))
        self._s3_resource = env_session.resource('s3')
        self.__progress_total = 0
        self.lock = Lock()

    @property
    def progress_total(self):
        with self.lock:
            return self.__progress_total

    def get_buckets(self) -> List[str]:
        """
        :return: List[str] = A list of bucket names for the account linked to the s3 client.
        """
        response = self._s3.list_buckets()

        assert 'Buckets' in response, "No buckets found in S3 response."

        buckets = response.get('Buckets', [])

        # Returns bucket names and strips out missing bucket names if any (would be probably rare or impossible)
        return [bucket.get('Name') for bucket in buckets if bucket.get('Name')]

    def get_folders(self, bucket_name: str) -> List[str]:
        """
        Return top level folders in the given S3 bucket.
        :param bucket_name: S3 bucket to search
        :return: List[str] - A list of folders that live in the top level of a S3 bucket.
        """

        paginator = self._s3.get_paginator('list_objects')
        result = paginator.paginate(Bucket=bucket_name, Delimiter='/')
        folders = []
        for prefix in result.search('CommonPrefixes'):
            folders.append(prefix.get('Prefix'))

        return folders

    def get_folders_recursive(self, bucket_name: str, folder_prefix: str = None, max_recursion_depth: int = 500,
                              recursion_depth: int = 0, max_folders_per_recurse: int = 500) -> Tuple[List[str], int]:
        """
        Find all subfolders in an S3 bucket by recursively iterating through each folder.
        :param bucket_name: Bucket to search
        :param folder_prefix: Used for recursive searches
        :param max_recursion_depth: Tunable parameter that allows control over recursion depth.
        :param recursion_depth: DO NOT PASS THIS PARAM. Keeps track of recursion depth to prevent bucket traversal
               going on FOREVER
        :param max_folders_per_recurse: Define a maximum # of folders to find per recursion depth. This prevents
        a single directory with a billion subdirs from holding up the recursion indefinitely. Set to 0 for infinite.

        :return: List[str] - a List of folders found in the S3 bucket.
        """

        recursion_depth = recursion_depth + 1
        paginator = self._s3.get_paginator('list_objects')
        new_folders, all_folders = [], []
        if not folder_prefix:
            result = paginator.paginate(Bucket=bucket_name, Delimiter='/')
        else:
            result = paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix, Delimiter='/')

        added_count = 0
        with ThreadPoolExecutor(max_workers=100) as pool:
            for prefix in result.search('CommonPrefixes'):
                if prefix:  # Prefix can sometimes be None
                    new_folders.append(prefix.get('Prefix'))
                    log.info(f"Adding folder: {prefix} - #{added_count}")
                    added_count += 1

            all_futures = []
            all_folders = new_folders.copy()
            if recursion_depth < max_recursion_depth:
                count = 0
                for folder in new_folders:
                    count = count + 1
                    if count < max_folders_per_recurse or max_folders_per_recurse == 0:
                        future = pool.submit(self.get_folders_recursive, bucket_name=bucket_name,
                                             folder_prefix=folder, max_recursion_depth=max_recursion_depth,
                                             recursion_depth=recursion_depth)
                        all_futures.append(future)
                    else:
                        log.info("Hit max recursion limit, skipping more recursion to search for more folders.")
                        break

                for future in as_completed(all_futures):
                    next_level, traversed_depth = future.result()
                    all_folders = all_folders + next_level
                    recursion_depth = traversed_depth if traversed_depth > recursion_depth else recursion_depth

        log.info(f"Returning from recursion into: {folder_prefix}")
        return sorted(list(set(all_folders))), recursion_depth

    def __list_progress_bar(self, file_count, enable_output: bool = True):
        for i in tqdm(range(0, file_count), disable=not enable_output, desc="Aggregating files...    ",
                      unit="folders aggregated."):
            while self.__progress_total < i:
                time.sleep(.1)

    def list_files(self, bucket_name: str, folder_prefix: str, folder_filter: str = None, enable_output=False,
                   max_recursion_depth: int = 50):
        """
        Return a list of all files in a bucket/folder prefix. The file names are the full path, including the prefix.
            Standard list with pagination will be very slow on large folders. This approach will return faster across
            large data sets by breaking up lists by each folder and running concurrently.
        :param bucket_name: bucket_name to query
        :param folder_prefix: some/path/to/query/ - folder heirarchy to query
        :param folder_filter: Optional[str] - only list files in folders that match this filter string. Wildcards (*)
                accepted.
        :param enable_output: Turns out printing details of search during search process to stdout.
        :param max_recursion_depth: Depth of folders to traverse while listing files.
        :return: List[str] List of file paths in S3 that match.
        """

        start_time  = time.time()
        paginator = self._s3.get_paginator('list_objects')
        all_files = []

        subfolders, depth_reached = self.get_folders_recursive(bucket_name, folder_prefix,
                                                               max_recursion_depth=max_recursion_depth)

        log.info(f'Found {len(subfolders)} searchable subfolders.')
        subfolders.append(folder_prefix)
        enable_output and print(f"Found {len(subfolders)} folders that could be searched.")

        # Filter our all non-matching folder_filter
        if folder_filter:
            subfolders = [x for x in subfolders if re.match(f'.*({folder_filter.replace("*", ".*")}).*', x)]
            enable_output and print(f"Searching {len(subfolders)} folders after filtering applied."
                                    f" Aggregating searchable file list.")

        futures = set()
        with ThreadPoolExecutor(max_workers=100) as pool:
            pool.submit(self.__list_progress_bar, len(subfolders), enable_output)

            for folder in subfolders:
                futures.add(pool.submit(paginator.paginate, Bucket=bucket_name, Delimiter='/', Prefix=folder))

            for future in as_completed(futures):
                result = future.result()
                self.__progress_total = self.__progress_total + 1
                for content in result.search("Contents"):
                    if content:
                        all_files.append(content.get('Key'))

            all_files = [file for file in all_files if file]  # Remove None if exists.

            self.__progress_total = 0

            log.info(f"List completed in {round(time.time() - start_time, 2)} seconds.")
            return sorted(list(set(all_files)))  # Sort, dedupe, and return

    def file_matches(self, bucket_name: str, s3_path: str, search_string: str, ignore_case=False) \
            -> Union[S3MatchResult]:
        """
        Raises an ValueError if the file provided is of an unsearchable type.

        Searches a file in S3 for the matching search_string. The search_string may provide wildcards (*)

        :param bucket_name: bucket of s3 file
        :param s3_path: path to file in s3 bucket
        :param search_string: String to match on. For instance: "foo" or "foo*bar"
        :return: Hydrated S3MatchResult object
        """
        file = self._s3_resource.Object(bucket_name, s3_path)
        file_suffix_searchable = True in [file.key.lower().endswith(item) for item in self._SEARCHABLE_SUFFIXES]
        file_type_searchable = file.content_type.lower() in self._SEARCHABLE_CONTENT_TYPES

        if not file_type_searchable and not file_suffix_searchable:
            return S3MatchResult(s3_path, None, None, skipped=True)

        previous_line = ''
        for line in file.get()['Body'].iter_lines(chunk_size=4096):
            flags = re.IGNORECASE if ignore_case else 0
            current_line = line.decode()
            match_line = previous_line + current_line
            result = re.match(f'.*({search_string.replace("*", ".*")}).*', match_line, flags=flags)

            if result:
                matching_string = result[1]
                context_result = re.match(f'.*(.{{20}})({search_string.replace("*", ".*")})(.{{20}}).*',
                                          match_line, flags=flags)
                if context_result:
                    matching_context = f'{context_result[1]} {context_result[2]} {context_result[3]}'
                    return S3MatchResult(s3_path, matching_string, matching_context)
                else:
                    return S3MatchResult(s3_path, matching_string, None)
            else:
                previous_line = current_line

        return S3MatchResult(s3_path, None, None)

    def files_match(self, bucket_name: str, s3_paths: List[str], search_string: str, ignore_case=False) \
            -> List[S3MatchResult]:
        """
        For batch submitting match requests.
        """
        results = []
        for idx, path in enumerate(s3_paths):
            results.append(self.file_matches(bucket_name, path, search_string, ignore_case=ignore_case))
            with self.lock:
                self.__progress_total = self.__progress_total + 1

        return results

    def get_file_stream(self, bucket: str, s3_path: str) -> StreamingBody:
        """
        Returns a file stream object representing a file stream from S3.
        :param bucket: S3 bucket
        :param s3_path: Object path in S3
        :return: StreamingBody resouruce.
        """
        return self._s3_resource.Object(bucket, s3_path).get()['Body']

    def download_file(self, bucket: str, s3_path: str, destination: str):
        """
        Download a file locally
        :param destination: Local file path to save file to.
        """

        self._s3_resource.Object(bucket, s3_path).download_file(destination)
