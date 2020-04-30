from config.aws import *

# Consul Mappings
consul_port = 8500
saj = "saj"
pm = "pm"


consul_map = {
    dev: {
        saj: f"consul.figgydev.corp",
        pm: f"consul-pm.figgydev.com"
    },
    qa: {
        saj: f"consul.figgyqa.corp",
        pm: f"consul-pm.figgyqa.com"
    },
    stage: {
        saj: f"consul.figgystage.corp",
        pm: f"consul-pm.figgystage.com"
    },
    prod: {
        saj: f"consul.figgyprod.corp",
        pm: f"consul-pm.figgyprod.com"
    }
}
