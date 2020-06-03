class Figgy < Formula
    include Language::Python::Virtualenv

    desc: "This is the CLI that accompanies the `figgy` configuration management framework."
    homepage: "https://figgy.dev"
    url:
    sha256: "e15158e7b6e724398969d7b3add642c0ac58081718b890ff0f071aa90ca6292f"

    depends_on "python@3.8"

    resource "aws-google-auth" do
        url "https://files.pythonhosted.org/packages/71/8f/aedfa502bfef36a60bc7a7cb3b72a06717ed2ac853ad0bdee7c480828d39/aws-google-auth-0.0.35.tar.gz"
        sha256 "cd4d0ac28dd05ec587037c37a86e8b67c16c93028388121d3df215f3ab13e857"
    end

    resource "beautifulsoup4" do
        url "https://files.pythonhosted.org/packages/c6/62/8a2bef01214eeaa5a4489eca7104e152968729512ee33cb5fbbc37a896b7/beautifulsoup4-4.9.1.tar.gz"
        sha256 "73cc4d115b96f79c7d77c1c7f7a0a8d4c57860d1041df407dd1aae7f07a77fd7"
    end

    resource "boto3" do
        url "https://files.pythonhosted.org/packages/29/7f/5f76466f99177245e8fc405d6604b206ef85872817bed429a846d34d12d0/boto3-1.13.19.tar.gz"
        sha256 "c774003dc13d6de74b5e19d2b84d625da4456e64bd97f44baa1fcf40d808d29a"
    end

    resource "botocore" do
        url "https://files.pythonhosted.org/packages/ff/6b/1d6afcfe57bffd1fe874bd623efa52994f57cbaaebd971bde8f44cc126f7/botocore-1.16.21.tar.gz"
        sha256 "7bd43e2fdf579875e3d3073e25699f5e524cc36a1748c4aee7c9c626e3760b2b"
    end

    resource "certifi" do
        url "https://files.pythonhosted.org/packages/b8/e2/a3a86a67c3fc8249ed305fc7b7d290ebe5e4d46ad45573884761ef4dea7b/certifi-2020.4.5.1.tar.gz"
        sha256 "51fcb31174be6e6664c5f69e3e1691a2d72a1a12e90f872cbdb1567eb47b6519"
    end

    resource "chardet" do
        url "https://files.pythonhosted.org/packages/fc/bb/a5768c230f9ddb03acc9ef3f0d4a3cf93462473795d18e9535498c8f929d/chardet-3.0.4.tar.gz"
        sha256 "84ab92ed1c4d4f16916e05906b6b75a6c0fb5db821cc65e70cbd64a3e2a5eaae"
    end

    resource "click" do
        url "https://files.pythonhosted.org/packages/27/6f/be940c8b1f1d69daceeb0032fee6c34d7bd70e3e649ccac0951500b4720e/click-7.1.2.tar.gz"
        sha256 "d2b5255c7c6349bc1bd1e59e08cd12acbbd63ce649f2588755783aa94dfb6b1a"
    end

    resource "configparser" do
        url "https://files.pythonhosted.org/packages/e5/7c/d4ccbcde76b4eea8cbd73b67b88c72578e8b4944d1270021596e80b13deb/configparser-5.0.0.tar.gz"
        sha256 "2ca44140ee259b5e3d8aaf47c79c36a7ab0d5e94d70bd4105c03ede7a20ea5a1"
    end

    resource "docutils" do
        url "https://files.pythonhosted.org/packages/93/22/953e071b589b0b1fee420ab06a0d15e5aa0c7470eb9966d60393ce58ad61/docutils-0.15.2.tar.gz"
        sha256 "a2aeea129088da402665e92e0b25b04b073c04b2dce4ab65caaa38b7ce2e1a99"
    end

    resource "figgy" do
        url "https://files.pythonhosted.org/packages/ad/1b/addddb50d6b08ff2e1464069bd741361ab872e0c55ba1a236aa8acbcf9c2/figgy-0.2.0rc1.tar.gz"
        sha256 "4abc239dc8400e27b49b67d9c0f57da52ba0a3ff4b8bfbd2ee05bd9605e7bfb3"
    end

    resource "filelock" do
        url "https://files.pythonhosted.org/packages/14/ec/6ee2168387ce0154632f856d5cc5592328e9cf93127c5c9aeca92c8c16cb/filelock-3.0.12.tar.gz"
        sha256 "18d82244ee114f543149c66a6e0c14e9c4f8a1044b5cdaadd0f82159d6a6ff59"
    end

    resource "idna" do
        url "https://files.pythonhosted.org/packages/cb/19/57503b5de719ee45e83472f339f617b0c01ad75cba44aba1e4c97c2b0abd/idna-2.9.tar.gz"
        sha256 "7588d1c14ae4c77d74036e8c22ff447b26d0fde8f007354fd48a7814db15b7cb"
    end

    resource "importlib-metadata" do
        url "https://files.pythonhosted.org/packages/b4/1b/baab42e3cd64c9d5caac25a9d6c054f8324cdc38975a44d600569f1f7158/importlib_metadata-1.6.0.tar.gz"
        sha256 "34513a8a0c4962bc66d35b359558fd8a5e10cd472d37aec5f66858addef32c1e"
    end

    resource "jmespath" do
        url "https://files.pythonhosted.org/packages/3c/56/3f325b1eef9791759784aa5046a8f6a1aff8f7c898a2e34506771d3b99d8/jmespath-0.10.0.tar.gz"
        sha256 "b85d0567b8666149a93172712e68920734333c0ce7e89b78b3e987f71e5ed4f9"
    end

    resource "jsonpickle" do
        url "https://files.pythonhosted.org/packages/4c/73/8e58db7955e3b2d98935f55ed40fdb7de142e875ee94616afdea196b0bfa/jsonpickle-1.4.1.tar.gz"
        sha256 "e8d4b7cd0bd6826001a74377df1079a76ad8bae0f909282de2554164c837c8ba"
    end

    resource "keyring" do
        url "https://files.pythonhosted.org/packages/a6/52/eb8a0e13b54ec9240c7dd68fcd0951c52f62033d438af372831af770f7cc/keyring-21.2.1.tar.gz"
        sha256 "c53e0e5ccde3ad34284a40ce7976b5b3a3d6de70344c3f8ee44364cc340976ec"
    end

    resource "keyrings.alt" do
        url "https://files.pythonhosted.org/packages/de/95/b127128917fef9ace8d8bfa66f3e3a81915d3dfa295d5f06784bca0c9854/keyrings.alt-3.4.0.tar.gz"
        sha256 "91328ac4229e70b1d0061d21bf61d36b031a6b4828f2682e38c741812f6eb23d"
    end

    resource "lxml" do
        url "https://files.pythonhosted.org/packages/03/a8/73d795778143be51d8b86750b371b3efcd7139987f71618ad9f4b8b65543/lxml-4.5.1.tar.gz"
        sha256 "27ee0faf8077c7c1a589573b1450743011117f1aa1a91d5ae776bbc5ca6070f2"
    end

    resource "mfa" do
        url "https://files.pythonhosted.org/packages/2c/ae/4e0a6053c8a5394b9d4a283346c7d9f9c559a22ccd1118ed10db9a9919cc/mfa-0.1.1.tar.gz"
        sha256 "9c30da365f3f56ec8e921178b495b0fff1fbbe6dfd2877900d8e4ce3aabe84ba"
    end

    resource "npyscreen" do
        url "https://files.pythonhosted.org/packages/93/48/91b8321280f17d135918895b57f891f727be84a88f62fc62485a7039de00/npyscreen-4.10.5.tar.gz"
        sha256 "622ee0f9a5dae946e635b7c6e0f6d65e1ed3c9ea0d20b89dab7f58d580e5126e"
    end

    resource "onetimepass" do
        url "https://files.pythonhosted.org/packages/aa/b2/cb6832704aaf11ed0e471910a8da360129e2c23398d2ea3a71961a2f5746/onetimepass-1.0.1.tar.gz"
        sha256 "a569dac076d6e3761cbc55e36952144a637ca1b075c6d509de1c1dbc5e7f6a27"
    end

    resource "pexpect" do
        url "https://files.pythonhosted.org/packages/e5/9b/ff402e0e930e70467a7178abb7c128709a30dfb22d8777c043e501bc1b10/pexpect-4.8.0.tar.gz"
        sha256 "fc65a43959d153d0114afe13997d439c22823a27cefceb5ff35c2178c6784c0c"
    end

    resource "Pillow" do
        url "https://files.pythonhosted.org/packages/ce/ef/e793f6ffe245c960c42492d0bb50f8d14e2ba223f1922a5c3c81569cec44/Pillow-7.1.2.tar.gz"
        sha256 "a0b49960110bc6ff5fead46013bcb8825d101026d466f3a4de3476defe0fb0dd"
    end

    resource "prompt-toolkit" do
        url "https://files.pythonhosted.org/packages/69/19/3aa4bf17e1cbbdfe934eb3d5b394ae9a0a7fb23594a2ff27e0fdaf8b4c59/prompt_toolkit-3.0.5.tar.gz"
        sha256 "563d1a4140b63ff9dd587bda9557cffb2fe73650205ab6f4383092fb882e7dc8"
    end

    resource "ptyprocess" do
        url "https://files.pythonhosted.org/packages/7d/2d/e4b8733cf79b7309d84c9081a4ab558c89d8c89da5961bf4ddb050ca1ce0/ptyprocess-0.6.0.tar.gz"
        sha256 "923f299cc5ad920c68f2bc0bc98b75b9f838b93b599941a6b63ddbc2476394c0"
    end

    resource "pycrypto" do
        url "https://files.pythonhosted.org/packages/60/db/645aa9af249f059cc3a368b118de33889219e0362141e75d4eaf6f80f163/pycrypto-2.6.1.tar.gz"
        sha256 "f2ce1e989b272cfcb677616763e0a2e7ec659effa67a88aa92b3a65528f60a3c"
    end

    resource "pydantic" do
        url "https://files.pythonhosted.org/packages/97/24/f8e05f16433b3b5332b3e2cf9b4625692c09432c7a18aa1d735fecb80904/pydantic-1.5.1.tar.gz"
        sha256 "f0018613c7a0d19df3240c2a913849786f21b6539b9f23d85ce4067489dfacfa"
    end

    resource "pyhcl" do
        url "https://files.pythonhosted.org/packages/91/b0/dd4f1d01b77be3b66d9f550ed958b68fa553764be1d27c7d604906c06b42/pyhcl-0.4.4.tar.gz"
        sha256 "2d9b9dcdf1023d812bfed561ba72c99104c5b3f52e558d595130a44ce081b003"
    end

    resource "pyotp" do
        url "https://files.pythonhosted.org/packages/f7/15/395c4945ea6bc37e8811280bb675615cb4c2b2c1cd70bdc43329da91a386/pyotp-2.3.0.tar.gz"
        sha256 "fc537e8acd985c5cbf51e11b7d53c42276fee017a73aec7c07380695671ca1a1"
    end

    resource "python-dateutil" do
        url "https://files.pythonhosted.org/packages/be/ed/5bbc91f03fa4c839c4c7360375da77f9659af5f7086b7a7bdda65771c8e0/python-dateutil-2.8.1.tar.gz"
        sha256 "73ebfe9dbf22e832286dafa60473e4cd239f8592f699aa5adaf10050e6e1823c"
    end

    resource "pytz" do
        url "https://files.pythonhosted.org/packages/f4/f6/94fee50f4d54f58637d4b9987a1b862aeb6cd969e73623e02c5c00755577/pytz-2020.1.tar.gz"
        sha256 "c35965d010ce31b23eeb663ed3cc8c906275d6be1a34393a1d73a41febf4a048"
    end

    resource "requests" do
        url "https://files.pythonhosted.org/packages/f5/4f/280162d4bd4d8aad241a21aecff7a6e46891b905a4341e7ab549ebaf7915/requests-2.23.0.tar.gz"
        sha256 "b3f43d496c6daba4493e7c431722aeb7dbc6288f52a6e04e7b6023b0247817e6"
    end

    resource "s3transfer" do
        url "https://files.pythonhosted.org/packages/50/de/2b688c062107942486c81a739383b1432a72717d9a85a6a1a692f003c70c/s3transfer-0.3.3.tar.gz"
        sha256 "921a37e2aefc64145e7b73d50c71bb4f26f46e4c9f414dc648c6245ff92cf7db"
    end

    resource "six" do
        url "https://files.pythonhosted.org/packages/6b/34/415834bfdafca3c5f451532e8a8d9ba89a21c9743a0c59fbd0205c7f9426/six-1.15.0.tar.gz"
        sha256 "30639c035cdb23534cd4aa2dd52c3bf48f06e5f4a941509c8bafd8ce11080259"
    end

    resource "soupsieve" do
        url "https://files.pythonhosted.org/packages/3e/db/5ba900920642414333bdc3cb397075381d63eafc7e75c2373bbc560a9fa1/soupsieve-2.0.1.tar.gz"
        sha256 "a59dc181727e95d25f781f0eb4fd1825ff45590ec8ff49eadfd7f1a537cc0232"
    end

    resource "sty" do
    url ""
    sha256 ""
    end

    resource "tabulate" do
        url "https://files.pythonhosted.org/packages/57/6f/213d075ad03c84991d44e63b6516dd7d185091df5e1d02a660874f8f7e1e/tabulate-0.8.7.tar.gz"
        sha256 "db2723a20d04bcda8522165c73eea7c300eda74e0ce852d9022e0159d7895007"
    end

    resource "tqdm" do
        url "https://files.pythonhosted.org/packages/3b/42/d14dda3dc578485ec6e24d66fac5b731b2a4c5441db0e2fdc31672864115/tqdm-4.46.0.tar.gz"
        sha256 "4733c4a10d0f2a4d098d801464bdaf5240c7dadd2a7fde4ee93b0a0efd9fb25e"
    end

    resource "tzlocal" do
        url "https://files.pythonhosted.org/packages/ce/73/99e4cc30db6b21cba6c3b3b80cffc472cc5a0feaf79c290f01f1ac460710/tzlocal-2.1.tar.gz"
        sha256 "643c97c5294aedc737780a49d9df30889321cbe1204eac2c2ec6134035a92e44"
    end

    resource "urllib3" do
        url "https://files.pythonhosted.org/packages/05/8c/40cd6949373e23081b3ea20d5594ae523e681b6f472e600fbc95ed046a36/urllib3-1.25.9.tar.gz"
        sha256 "3018294ebefce6572a474f0604c2021e33b3fd8006ecd11d62107a5d2a963527"
    end

    resource "wcwidth" do
        url "https://files.pythonhosted.org/packages/97/23/3c0fde825b1c6a015e7360e105da2bdf3034fe670ede8f03d21194c1b910/wcwidth-0.2.3.tar.gz"
        sha256 "edbc2b718b4db6cdf393eefe3a420183947d6aa312505ce6754516f458ff8830"
    end

    resource "websocket_client" do
        url "https://files.pythonhosted.org/packages/8b/0f/52de51b9b450ed52694208ab952d5af6ebbcbce7f166a48784095d930d8c/websocket_client-0.57.0.tar.gz"
        sha256 "d735b91d6d1692a6a181f2a8c9e0238e5f6373356f561bb9dc4c7af36f452010"
    end

    resource "zipp" do
        url "https://files.pythonhosted.org/packages/ce/8c/2c5f7dc1b418f659d36c04dec9446612fc7b45c8095cc7369dd772513055/zipp-3.1.0.tar.gz"
        sha256 "c599e4d75c98f6798c509911d08a22e6c021d074469042177c8c86fb92eefd96"
    end

    resource "zipstream" do
        url "https://files.pythonhosted.org/packages/1a/a4/58f0709cef999db1539960aa2ae77100dc800ebb8abb7afc97a1398dfb2f/zipstream-1.1.4.tar.gz"
        sha256 "2ef24b9150c93429b172750c4890b5ab28c1317892e11727afeff986ad2a3506"
    end

    def install
        virtualenv_install_with_resources
    end

    test do
        output = shell_output("#{bin}figgy --version")
        assert output.include? "Version", "Unable to validate successful install. Figgy"
    end
end