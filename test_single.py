import os
import time
import argparse
import torch
from tqdm.auto import tqdm

from utils.misc import *
from utils.denoise import *
from utils.transforms import *
from models.denoise import *

USER = "yuki"
# USER = "yonelab"
MIN_FRAME = 147
MAX_FRAME = 392

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--ckpt', type=str, default='./pretrained/ckpt.pt')
# parser.add_argument('--input_xyz', type=str,
#                     default='./data/examples/PUNet_10000_poisson_0.02/duck.xyz')
# parser.add_argument('--output_xyz', type=str,
#                     default='./data/examples/PUNet_10000_poisson_0.02/duck_denoised.xyz')
parser.add_argument('--device', type=str, default='cuda')
parser.add_argument('--seed', type=int, default=2020)
args = parser.parse_args()
seed_all(args.seed)

# Model
ckpt = torch.load(args.ckpt, map_location=args.device)
model = DenoiseNet(ckpt['args']).to(args.device)
model.load_state_dict(ckpt['state_dict'])

for frame in tqdm(range(MIN_FRAME, MAX_FRAME+1)):

    INPUT_XYZ = "/home/"+USER + \
        "/workspace/lidar_data/run_pcd_intensity/human_only/xyz/LIV_run_human" + \
        str(frame)+".xyz"
    OUTPUT_XYZ = "/home/"+USER + \
        "/workspace/lidar_data/run_pcd_intensity/human_only/xyz_denoised/LIV_run_human" + \
        str(frame)+".xyz"

    # Point cloud
    pcl = np.loadtxt(INPUT_XYZ)
    pcl = torch.FloatTensor(pcl)
    pcl, center, scale = NormalizeUnitSphere.normalize(pcl)
    pcl = pcl.to(args.device)

    print('[INFO] Start denoising...')
    try:
        pcl_denoised = patch_based_denoise(model, pcl).cpu()
        pcl_denoised = pcl_denoised * scale + center
        print('[INFO] Finished denoising.')

        print('[INFO] Saving denoised point cloud to: %s' % OUTPUT_XYZ)
        np.savetxt(OUTPUT_XYZ, pcl_denoised, fmt='%.8f')
    except RuntimeError as e:
        pass
