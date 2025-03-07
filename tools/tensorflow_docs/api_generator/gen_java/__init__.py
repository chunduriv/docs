# Lint as: python3
# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Generate javadoc-doclava reference docs for tensorflow.org."""

import os
import pathlib
import subprocess
from typing import Mapping, Optional

from tensorflow_docs.api_generator.gen_java import processing

import yaml


class Formatter(yaml.dumper.Dumper):
  pass


def _dict_representer(dumper, data):
  """Force yaml to output dictionaries in order, not alphabetically."""
  return dumper.represent_dict(data.items())


Formatter.add_representer(dict, _dict_representer)

# __file__ is the path to this file
GEN_JAVA_DIR = pathlib.Path(__file__).resolve().parent

TEMPLATES = GEN_JAVA_DIR / 'templates'
DOCLAVA_FOR_TF = GEN_JAVA_DIR / 'run-javadoc-for-tf.sh'


def gen_java_docs(package: str,
                  source_path: pathlib.Path,
                  output_dir: pathlib.Path,
                  site_path: pathlib.Path,
                  script_path: pathlib.Path = DOCLAVA_FOR_TF,
                  section_labels: Optional[Mapping[str, str]] = None) -> None:
  """Generate tensorflow.org java-docs for `package`."""
  for path in source_path, output_dir, script_path, TEMPLATES:
    assert path.is_absolute(), 'All paths used in doc-gen must be absolute'

  os.environ['PACKAGE'] = package
  os.environ['SOURCE_PATH'] = str(source_path)
  os.environ['OUTPUT_DIR'] = str(output_dir)
  os.environ['SITE_PATH'] = str(pathlib.Path('/') / site_path)
  os.environ['TEMPLATES'] = str(TEMPLATES)
  subprocess.check_call(['bash', script_path])

  yaml_path = pathlib.Path(output_dir) / '_toc.yaml'
  yaml_content = yaml_path.read_text()
  yaml_data = yaml.safe_load(yaml_content)
  if section_labels:
    yaml_data = processing.add_package_headings(yaml_data, package,
                                                section_labels)
  yaml_content = yaml.dump(yaml_data, Dumper=Formatter)
  yaml_path.write_text(yaml_content)
