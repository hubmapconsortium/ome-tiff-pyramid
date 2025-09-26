cwlVersion: v1.1
class: CommandLineTool
label: Crop image to tissue selection, either detected or read from GeoJSON

requirements:
  DockerRequirement:
    dockerPull: hubmap/ome-tiff-pyramid:latest
    dockerOutputDirectory: "/output"

baseCommand: ["python", "/opt/crop_input_image.py", "--debug"]

inputs:
  ometiff_file:
    type: File
    inputBinding:
      position: 0
  base_directory:
    type: string
    inputBinding:
      position: 1
  invert_geojson_mask:
    type: boolean?
    inputBinding:
      position: 2
      prefix: "--invert-geojson-mask"

outputs:
  crop_ome_tiff:
    type: File
    outputBinding:
      glob: "/output/*.ome.tif"
  crop_debug_data:
    type: Directory?
    outputBinding:
      glob: "/output/crop-debug"
