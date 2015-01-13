import os
import unittest
import models

home = os.path.expanduser("~")

data_directory = 'Documents/data/' 
path = '999'
row = '999'
time = '999999'
l8 = 'LC8'
receiving_station = 'LGN'
archive_version_number = '00'
product_level = '_L2'
file_type = 'nc'
parent_directory = l8+path+row+time+receiving_station+archive_version_number
file_name = parent_directory+product_level

class DirectoryModelTest(unittest.TestCase):

    def test_directory(self):
        """Test if the Directory model works."""
        test_directory = models.DirectoryModel(data_directory, path, row, time)
        test_directory.setup_dir()
        print(test_directory.dir_name)
        self.assertEqual(test_directory.dir_name, os.path.join(home, data_directory, l8, path, row, l8+path+row+time+receiving_station+archive_version_number))

class FileModelTest(unittest.TestCase):

    def test_file(self):
        "Test if the file model works"
        test_file = models.FileModel(data_directory, path, row, time, file_type)
        test_file.setup_file()
        print(test_file.full_path)
        self.assertEqual(test_file.full_path, os.path.join(home, data_directory, l8, path, row, l8+path+row+time+receiving_station+archive_version_number, '') + file_name+'.'+file_type)

class NetcdfModelTest(unittest.TestCase):

    def test_netcdf_file(self):
        """Test if the netcdf file works"""
        test_netcdf_file = models.NetcdfModel(data_directory, path, row, time)
        test_netcdf_file.setup_file()
        print(test_netcdf_file.full_path)
        self.assertEqual(test_netcdf_file.full_path, os.path.join(home, data_directory, l8, path, row, l8+path+row+time+receiving_station+archive_version_number, '') + file_name+'.'+file_type)


if __name__ == '__main__':
    unittest.main()