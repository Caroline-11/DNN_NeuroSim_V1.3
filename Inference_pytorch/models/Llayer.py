from utee import misc
print = misc.logger.info
import torch.nn as nn
from modules.quantization_cpu_np_infer import QConv2d,  QLinear
from modules.floatrange_cpu_np_infer import FConv2d, FLinear
import torch

class Llayer(nn.Module):
    def __init__(self, args, logger):
        super(Llayer, self).__init__()
        self.linear = QLinear(in_features= 4, out_features= 4, 
                                logger=logger, wl_input = args.wl_activate,wl_activate=args.wl_activate,wl_error=args.wl_error,
                                wl_weight=args.wl_weight,inference=args.inference,onoffratio=args.onoffratio,cellBit=args.cellBit,
                                subArray=args.subArray,ADCprecision=args.ADCprecision,vari=args.vari,t=args.t,v=args.v,detect=args.detect,target=args.target, 
                                name='FCL_', model = args.model)
        # define weight matrix 
        weight_matrix = input_matrix = torch.tensor([
            [1,2,3,4],
            [5,6,7,8],
            [9,10,11,12],
            [13,14,15,16]
        ], dtype=torch.float32)
        self.weight = nn.Parameter(weight_matrix)
    
    def forward(self, x):
        x = self.linear(x)
        return x

def llayer(args, logger):
    model = Llayer(args,logger = logger)
    return model