# Copyright 2020-2022 OpenDR European Project
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


from opendr.perception.pose_estimation import LightweightOpenPoseLearner
import argparse
from os.path import join
from opendr.engine.datasets import ExternalDataset

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx", help="Use ONNX", default=False, action="store_true")
    parser.add_argument("--device", help="Device to use (cpu, cuda)", type=str, default="cuda")
    parser.add_argument("--accelerate", help="Enables acceleration flags (e.g., stride)", default=False,
                        action="store_true")
    args = parser.parse_args()

    onnx, device, accelerate = args.onnx, args.device, args.accelerate
    if accelerate:
        stride = True
        stages = 0
        half_precision = True
    else:
        stride = False
        stages = 2
        half_precision = False

    pose_estimator = LightweightOpenPoseLearner(device=device, num_refinement_stages=stages,
                                                mobilenet_use_stride=stride,
                                                half_precision=half_precision)
    pose_estimator.download(path=".", verbose=True)
    pose_estimator.load("openpose_default")

    if onnx:
        pose_estimator.optimize()

    # Download a sample dataset
    pose_estimator.download(path=".", mode="test_data")

    eval_dataset = ExternalDataset(path=join("temp", "dataset"), dataset_type="COCO")

    results_dict = pose_estimator.eval(eval_dataset, use_subset=False, verbose=True, silent=True,
                                       images_folder_name="image", annotations_filename="annotation.json")

    print("Evaluation results = ", results_dict)
