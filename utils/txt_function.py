# -*- coding: utf-8 -*-
import pandas as pd
import os
import csv
import glob
from datetime import datetime
from PyQt5.QtCore import QObject


class TxtFunction(QObject):
    """ Write data to txt file """

    def __init__(self) -> None:
        super().__init__()
        
    def setUnits(self, units):
        self.units = units

    def txtUpdate(self, sequence_num, method, name, x_show, y_show):
        # user the sequence_num to choose the txt
        txtname = f'./data/{sequence_num}.csv'

        def txtCreat(method, name):
            """ creat a new txt """
            # generate the title_list to be a header in the txt
            title_list = []
            for i in range(len(name)):
                # get name and method
                temp_name = name[i]
                temp_method = method[i]
                # reconstruct them as name_method, e.g., SR830_Frequency
                temp_title = temp_name + '_' + temp_method
                # append the title_list
                title_list.append(temp_title)

            self.txtWriter(txtname, title_list, 'w')

        def txtSaver(x_show, y_show):
            # copy y_show list to temp_data
            temp_data = y_show.copy()
            # insert the x value to the y side
            temp_data.insert(0, x_show[0])
            # open file
            self.txtWriter(txtname, temp_data, 'a')

        # if the seq_num equals to txt_count, it means it has to creat a new txt before writing
        if os.path.exists(txtname):
            # write the data
            txtSaver(x_show, y_show)
        else:
            # creat empty txt
            txtCreat(method, name)
            # write the data
            txtSaver(x_show, y_show)

    # =============================================================================
    # Merge file. activate when stopping
    # =============================================================================

    def txtMerger(self, file_name, sequence_length, channel_num):
        # channel_num is the total number of reading channel + 1 X channel
        # we get the channel number from y_show + 1
        # Check if the next file is incompleted
        if os.path.exists(f'./data/{sequence_length}.csv'):
            sequence_length += 1
        # creat a empty list named title to record <CHA> S1C1 S1C2....
        title = []
        for j in range(sequence_length):
            for k in range(channel_num):
                if k == 0:
                    title.append('<CHA>')
                else:
                    title.append('S%dC%d' % (j+1, k))
        # creat a empty list name temp_txt to append every sub txt file
        temp_txt = []
        for i in range(sequence_length):
            if os.path.exists(f'./data/{i}.csv'):
                temp_txt.append(pd.read_csv(f'./data/{i}.csv'))
        # open the file and writre the units
        # Example: For two read channels result, we will have the units_list as ["", "y1", "y2", "", "y1", "y2", ... ] 
        # Add the unit of x axis (empty unit) to the units lists from read channels and multiple the units_list sequence_length
        units_list = ([""] + self.units) * sequence_length
        output_name = f'{file_name}.csv'
        # open the file and write the title and units
        with open(output_name, 'w', newline='') as header_csv:
            writer = csv.writer(header_csv)
            writer.writerow(title)
            writer.writerow(units_list)
        # form the final dataframe from temp_txt
        if temp_txt:
            final_df = pd.concat(temp_txt, axis=1)
            # write the dataframe to the same txt file
            final_df.to_csv(output_name, header=True, index=False, mode='a')

    def txtDeleter(self):
        txt_files = glob.glob('./data/*[0-9].csv')
        for file in txt_files:
            os.remove(file)

    def txtWriter(self, txtname, txtdata, option):
        # open file with name "txtname"
        # option can be 'a' or 'w' depending the way of usage
        with open(txtname, option, newline='') as data_csv:
            writer = csv.writer(data_csv)
            writer.writerow(txtdata)
        

    def recordSteps(self, steps):
        with open('./ui/asset/step.txt', 'w') as f:
            date = str(datetime.now())[:19]
            f.write(f'Created on\t{date}\n')
            f.write(f'Connection (Name/Type/Address) :\n')
            for element in steps[0]:
                if element == ".":
                    f.write('\n')
                else:
                    f.write(f'{element}\t')
            f.write(f'Control (Level/Name/Type/Property/Target/Speed/Increment/Ins_lable) :\n')
            for element in steps[1]:
                if element == ".":
                    f.write('\n')
                else:
                    f.write(f'{element}\t')
            f.write(f'Read (Name/Type/Property/Magnification/Unit) :\n')
            for element in steps[2]:
                if element == ".":
                    f.write('\n')
                else:
                    f.write(f'{element}\t')
            f.write(f'File address:\n{steps[3][0]}')
            f.write(f'\nFile name:\n{steps[4][0]}')


if __name__ == '__main__':
    channel_num = 9
    sequence_length = 37
    file_name = 'B+-8(0.5)  Vtg=+-15V  SD 9-5  Rxx 6-7  Rxy 8-10  T1.6K 3'
    txt = TxtFunction()
    txt.units = ['']
    txt.txtMerger(file_name, sequence_length, channel_num)
