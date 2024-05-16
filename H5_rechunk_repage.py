#!/usr/bin/env python
# coding: utf-8

# In[1]:


import h5py

# Example inputs
#source_file_path = '/Users/earmstro/HDF5_Aggregation/data/NISAR_L2_PR_GSLC_001_005_A_219_2005_DHDH_A_20081127T060959_20081127T061015_P01101_F_N_J_001.h5'
#target_file_path = '/Users/earmstro/HDF5_Aggregation/data/NISAR_L2_PR_GSLC_001_005_A_219_2005_DHDH_A_20081127T060959_20081127T061015_P01101_F_N_J_001.rechunk.h5'

# set the page size for the Page Strategy
#hdf_page_size = 2048*2048  # 4 MiB size

# set the chunk size
#chunk = 512




def print_dataset_info(filename):
    try:
        with h5py.File(filename, 'r') as hdf_file:
            print("Datasets in HDF5 file:", filename)
            print("----------------------------")
            hdf_file.visititems(print_dataset)
    except Exception as e:
        print("Error:", e)

def print_dataset(name, obj):
    if isinstance(obj, h5py.Dataset):
        print("Dataset:", name)
        print("Dimensions:", obj.shape)
        print("Chunk Sizes:", obj.chunks)
        print("----------------------------")

# use the "page" strategy with defined page size for the new HDF file        
def copy_datasets(source_file, target_file, chunk, hdf_page_size):
    try:
        with h5py.File(source_file, 'r') as source, h5py.File(target_file, 'w', fs_strategy="page", fs_page_size=hdf_page_size) as target:                   
            source.visititems(lambda name, obj: copy_dataset(name, obj, target, chunk))
    except Exception as e:
        print("Error:", e)

def copy_dataset(name, obj, target, chunk):
    if isinstance(obj, h5py.Dataset):
        source_dataset = obj
        #print(" dataset name is ", source_dataset.name )
          
        # Copy datasets to target    
        if source_dataset.size == 1:  # Scalar dataset 
            target_dataset = target.create_dataset(name, data=source_dataset[()])       
        elif source_dataset.ndim == 2 and source_dataset.shape[0] >= chunk and source_dataset.shape[1] >= chunk:
            target_dataset = target.create_dataset(name, data=source_dataset[:], chunks=(chunk,chunk),
                                                compression=source_dataset.compression,
                                                compression_opts=source_dataset.compression_opts) 
        else:
            target_dataset = target.create_dataset(name, data=source_dataset[:],
                                               compression=source_dataset.compression,
                                               compression_opts=source_dataset.compression_opts)         
        # Copy the attributes
        for attr_name, attr_value in source_dataset.attrs.items():
            target_dataset.attrs[attr_name] = attr_value

if __name__ == "__main__":
    # input/output files
    source_file_path = input("Enter the path to the source HDF5 file: ")
    target_file_path = input("Enter the path to the target HDF5 file: ")
    
   # chunk size
    chunk = int(input("Enter the chunk pixel size (e.g, 512): "))
    
    # Page size for file space management strategy
    hdf_page_size = int(input("Enter the HDF5 Page Size in bytes (e.g., 2048*2048 == 4194304 bytes): "))

    
    print_dataset_info(source_file_path)
    
    print(f" copying datasets from source to target . . ." )

    copy_datasets(source_file_path, target_file_path, chunk, hdf_page_size)
    #copy_datasets(source_file_path, target_file_path)
    
    print(f" DONE" )


# In[ ]:




