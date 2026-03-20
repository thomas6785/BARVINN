import numpy as np

def read_binary_file(filename,precision=8):
    """
    Reads in a file of binary numbers (not a binary file, a text file with lots of 0s and 1s in it) and converts to a Numpy array
    Also handles MSB transposed format
    """
    with open(filename,mode="r") as file:
        lines = file.readlines()

    ret = []
    for i in range(0,len(lines),precision):
        linegroup = lines[i:i+precision]
        values = [0 for i in range(len(linegroup[0].strip()))]
        for line in linegroup:
            values = [2*a+int(b) for a,b in zip(values,line.strip())]
        ret.append(values)
    return np.array(ret)

def read_hex_file(filename,precision=16,skiplines=8192):
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

img = read_binary_file("/home/tudentstudent/BARVINN_3/sparse_32x32_image.bin")
weights = read_binary_file("/home/tudentstudent/BARVINN_3/sparse_3x3_kernel_8bits.bin")

# img is 1024 x 64
img = img.reshape(32,32,64) # reshape to be a 32x32 image with 64 channels
# weights is 9 x 4096
weights = weights.reshape(3,3,64,64) # reshape to be a 3x3 kernel with 64 channels

# perform convolution in numpy
output = np.zeros((30,30,64),dtype=np.int32) # output is 30x30 with 64 channels
for i in range(30):
    for j in range(30):
        for k in range(64):
            output[i,j,k] = np.sum(img[i:i+3,j:j+3,:] * weights[:,:, :,k])

#print(output[0][0])