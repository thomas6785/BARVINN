import numpy as np
from pathlib import Path

np.random.seed(0) # for reproducibility

# --- Parameters ---
H = W = 32          # Input spatial dimensions (height and width), parametrisable
C_in = 64           # Number of input channels
C_out = 64          # Number of output channels
K = 3               # Kernel spatial size (K x K)

# --- Input Feature Map  (NHWC layout) ---
# Shape: (H, W, C_in)
#   H, W  – spatial height and width (equal, parametrisable)
#   C_in  – number of input channels (e.g. 64)
input_feature_map = np.zeros((H, W, C_in), dtype=np.float32)

# --- Convolution Kernel (Filter Bank, HWIO layout) ---
# Shape: (K, K, C_in, C_out)
#   K, K  – spatial extent of each filter (e.g. 3 x 3)
#   C_in  – number of input channels each filter acts on (e.g. 64)
#   C_out – number of output channels / filters (e.g. 64)
kernel = np.zeros((K, K, C_in, C_out)).astype(np.float32)


# --- Convolution Function (NHWC) ---
def conv2d(input: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Apply a 2-D convolution (no padding, stride=1) in NHWC / HWIO layout.

    Parameters
    ----------
    input : np.ndarray, shape (H, W, C_in)
        Input feature map in NHWC format (single image, no batch dim).
    kernel : np.ndarray, shape (kH, kW, C_in, C_out)
        Convolution filter bank in HWIO format.

    Returns
    -------
    output : np.ndarray, shape (H_out, W_out, C_out)
        where H_out = H - kH + 1, W_out = W - kW + 1
    """
    kH, kW, c_in, c_out = kernel.shape
    h_in, w_in, _ = input.shape
    h_out = h_in - kH + 1
    w_out = w_in - kW + 1

    output = np.zeros((h_out, w_out, c_out), dtype=input.dtype)

    for i in range(h_out):
        for j in range(w_out):
            patch = input[i:i+kH, j:j+kW, :]               # (kH, kW, C_in)
            for oc in range(c_out):
                output[i, j, oc] = np.sum(patch * kernel[:, :, oc, :])

    return output


# --- Run convolution ---
output_feature_map = conv2d(input_feature_map, kernel)

# --- Summary ---
print(f"Input feature map shape : {input_feature_map.shape}  "
      f"(height={H}, width={W}, channels={C_in})  [NHWC]")
print(f"Kernel shape            : {kernel.shape}  "
      f"(kH={K}, kW={K}, in_channels={C_in}, out_channels={C_out})  [HWIO]")
print(f"Output feature map shape: {output_feature_map.shape}  "
      f"(height={H-K+1}, width={W-K+1}, channels={C_out})  [NHWC]")

def data_to_bin(feature_map, precision=8):
    """Convert a feature map to a binary string representation.

    Parameters
    ----------
    feature_map : np.ndarray, shape (H, W, C)
        Input feature map in NHWC format.
    precision : int
        Number of bits to represent each value (e.g. 8 for uint8).

    Returns
    -------
    binary_string : str
        A string of '0's and '1's representing the quantized feature map.
    """
    # Each row/column pair is represented by a 64 x precision matrix (64 channels, precision bits per value)

    out = ""

    for row in feature_map:
        for pixel in row:
            # pixel is 64 x 1 (64 channels)
            pixel_in_binary = [bin(int(i))[2:].zfill(precision) for i in pixel] # convert each value to binary string with leading zeros
            bin_chars = [list(i) for i in pixel_in_binary] # split each binary string into a list of characters
            bin_chars_t = np.transpose(bin_chars) # transpose to get precision x 64
            out += "\n".join("".join(i) for i in bin_chars_t) +"\n" # output the binary representation of the pixel (precision x 64)
    
    return out

def kernel_to_bin(kernel, precision=8):
    """Convert a convolution kernel to a binary string representation.

    Parameters
    ----------
    kernel : np.ndarray, shape (kH, kW, C_in, C_out)
        Convolution filter bank in HWIO format.
    precision : int
        Number of bits to represent each value (e.g. 8 for uint8).

    Returns
    -------
    binary_string : str
        A string of '0's and '1's representing the quantized kernel.
    """
    # Each row/column pair is represented by a 64 x precision matrix (64 input channels, precision bits per value)

    out = ""

    for row in kernel:
        for pixel in row:
            a = pixel.reshape(4096) # reshape to be 4096 x 1 (64x64 input-output channel combinations)
            pixel_in_binary = [bin(int(i))[2:].zfill(precision) for i in a] # convert each value to binary string with leading zeros
            bin_chars = [list(i) for i in pixel_in_binary] # split each binary string into a list of characters
            bin_chars_t = np.transpose(bin_chars) # transpose to get precision x 4096
            out += "\n".join("".join(i) for i in bin_chars_t) + "\n" # output the binary representation of the pixel
    
    return out

def bin_to_data(binary_string,precision=16):
    """Convert a binary string representation back to a feature map.

    Parameters
    ----------
    binary_string : str
        A string of '0's and '1's representing the quantized feature map.
    precision : int
        Number of bits that were used to represent each value (e.g. 8 for uint8).

    Returns
    -------
    feature_map : np.ndarray, shape (H, W, C)
        Output feature map in NHWC format.
    """
    # Each row/column pair is represented by a 64 x precision matrix (64 channels, precision bits per value)

    lines = binary_string.strip().split("\n")
    values = []
    for i in range(0,len(lines),precision):
        linegroup = lines[i:i+precision]
        value = [0 for i in range(len(linegroup[0].strip()))]
        for line in linegroup:
            value = [2*a+int(b) for a,b in zip(value,line.strip())]
        values.append(value)
    
    return np.array(values)

#test_kernel = np.random.randint(0,256,size=(3,3,64,64)).astype(np.uint32)
#test_input = np.random.randint(0,256,size=(32,32,64)).astype(np.uint32)

test_kernel = np.zeros((3,3,64,64)).astype(np.uint32)
test_input  = np.zeros((32,32,64)).astype(np.uint32)

for chan in range(64):
    for row in range(2):
        for col in range(2):
            test_kernel[row,col,chan,chan] = 1#np.random.randint(0,4)
            #           |   |   |    |
            #           |   |   |    INPUT channel
            #           |   |   OUTPUT channel
            #           |   COLUMN
            #           ROW

for chan in range(64):
    for row in range(32):
        for col in range(32):
            test_input[row,col,chan] = np.random.randint(0,8)
            #          |   |   |
            #          |   |   CHANNEL
            #          |   COLUMN
            #          ROW

# MVU will lose 11 bits of precision so let's add 11 here
test_input *= 2**5    # means max value in input is 7
test_kernel *= 2**6   # means max value in kernel is 3


#for i in range(3):
#    for j in range(3):
#        test_input[i,j,0] = np.random.randint(0,256)
#        test_kernel[i,j,0,0] = np.random.randint(0,256)

kernel_bin = kernel_to_bin(test_kernel, precision=8)
input_bin = data_to_bin(test_input, precision=8)

kernel_bin_path = "/home/tudentstudent/BARVINN/BARVINN/kernel_bin.txt"
input_bin_path  = "/home/tudentstudent/BARVINN/BARVINN/input_bin.txt"

with open(kernel_bin_path, mode="w") as f:
    f.write(kernel_bin.strip())
with open(input_bin_path, mode="w") as f:
    f.write(input_bin.strip())

print(f"Wrote kernel binary to {kernel_bin_path}")
print(f"Wrote input binary to {input_bin_path}")


def read_hex_file(filename="/home/tudentstudent/BARVINN/BARVINN/build/barvinn_0/sim-xsim/result.hex",precision=16,skiplines=8192):
    """
    Reads in a file of hex numbers (not a binary file, a text file with lots of hex digits in it) and converts to a Numpy array
    Also handles MSB transposed format
    """
    with open(filename,mode="r") as file:
        lines_hex = file.readlines()[8192:] # skip the first 8192 lines which are just input data
    lines = [bin(int(i,16))[2:].zfill(4*len(i.strip())) for i in lines_hex]
    
    ret = []
    for i in range(0,len(lines),precision):
        linegroup = lines[i:i+precision]
        values = [0 for i in range(len(linegroup[0].strip()))]
        for line in linegroup:
            values = [2*a+int(b) for a,b in zip(values,line.strip())]
        ret.append(values)
    return np.array(ret)

pred = conv2d(test_input, test_kernel) >> 11
input("Press ENTER to read results once simulation is complete...")
sim_out = read_hex_file()[:300].reshape(10,30,64)

assert np.all(sim_out[0:2,0:9,:]==pred[0:2,0:9,:]), "Test failed: simulated output does not match expected output"
print("Test passed")
