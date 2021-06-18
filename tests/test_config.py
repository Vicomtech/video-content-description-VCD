import os
import vcd.core as core
import vcd.schema as schema

openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
overwrite = False


def check_openlabel(openlabel, openlabel_file_name, force_write=False):
    if not os.path.isfile(openlabel_file_name) or force_write:
        openlabel.save(openlabel_file_name)

    openlabel_read = core.OpenLABEL(openlabel_file_name, validation=True)
    return openlabel_read.stringify() == openlabel.stringify()
