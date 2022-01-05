# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 16:45:34 2021
@author: Tsung-Lin
"""
import pandas as pd
import os

# to check if the sequence is new for creating txt
txt_count = 0


def txtUpdate(sequence_num, method, name, x_show, y_show):

    global txt_count
    # if the seq_num equals to txt_count, it means it has to creat a new txt before writing
    if sequence_num == txt_count:
        txt_count += 1
        # creat empty txt
        txtCreat(sequence_num, method, name)
        # write the data
        txtSaver(sequence_num, x_show, y_show)
    else:
        # write the data
        txtSaver(sequence_num, x_show, y_show)


def txtCreat(sequence_num, method, name):
    # user the sequence_num to choose the txt
    txtname = str(sequence_num) + '.txt'
    #
    title_list = []
    # generate the title_list to be a header in the txt
    for i in range(len(name)):
        # get name and method
        temp_name = name[i]
        temp_method = method[i]
        # reconstruct them as name_method, e.g., SR830_Frequency
        temp_title = temp_name + '_' + temp_method
        # append the title_list
        title_list.append(temp_title)

    txtWriter(txtname, title_list, 'w')


def txtSaver(sequence_num, x_show, y_show):
    # user the sequence_num to choose the txt
    txtname = str(sequence_num) + '.txt'
    # copy y_show list to temp_data
    # 我在這裡應該已經把y_show指派給temp_data
    temp_data = y_show.copy()
    # insert the x value to the y side
    temp_data.insert(0, x_show[0])
    # open file
    txtWriter(txtname, temp_data, 'a')

# =============================================================================
# Merge file. activate when stopping
# =============================================================================


def txtMerger(file_name, sequence_length, channel_num):
    # channel_num is the total number of reading channel + 1 X channel
    # we get the channel number from y_show + 1

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
        temp_txt.append(pd.read_csv("%d.txt" % i, delimiter="\t"))
    # open the file and write the title first
    txtWriter('%s.txt' % file_name, title, 'w')
    # form the final dataframe from temp_txt
    final_df = pd.concat(temp_txt, axis=1)
    # write the dataframe to the same txt file
    final_df.to_csv(r'%s.txt' % file_name, header=True,
                    index=False, sep='\t', mode='a')


def txtDeleter(sequence_length):
    for i in range(sequence_length):
        os.remove("%d.txt" % i)


def txtWriter(txtname, txtdata, option):
    # open file with name "txtname"
    # write data "txtdata" in and perform \n if necessary
    # option can be 'a' or 'w' depending the way of usage
    f = open(txtname, '%s' % option)
    for i, element in enumerate(txtdata):
        if i == len(txtdata) - 1:
            # write the last element and \n
            f.write(str(element))
            f.write('\n')
        else:
            # write the every element. sep = \tab
            f.write(str(element) + '\t')
    f.close()


if __name__ == '__main__':
    x_show = [0, 'SR830', 'frequency']
    y_show = [1, 2, 3]
    sequence_num = 0
    #      [[first sequence]]
    #      [[first sequence X, Y, Y, Y      ],[Second sequence X, Y, Y, Y     ]]
    name = ['SR830', 'SR830', 'SR830', 'SR830']
    method = ['frequency', 'phase', 'frequency', 'phase']
# =============================================================================
#     name = [['SR830','SR830','SR830','SR830'],['SR830','SR830','SR830','SR830']]
#     method = [['frequency', 'phase', 'frequency', 'phase'], ['magnitude', 'phase_1', 'magnitude', 'phase_1']]
#
# =============================================================================