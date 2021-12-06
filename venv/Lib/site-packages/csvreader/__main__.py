from csvreader import ReadCSV, WriteCSV
filename = input('Enter filename: ') + '.csv'
filename = filename.replace('..','.')
print(f'Filename: {filename}')
WriteCSV(filename, '1, MyName, MyResidence, myemail@example.com\n', mode = 'w')
print("Wrote 1, MyName, MyResidence, myemail@example.com\n into the file in w mode. Now writing in a mode...")
WriteCSV(filename, '2, MyName2, MyResidence2, myemail2@example.com\n', mode = 'a')
print('Wrote 2, MyName2, MyResidence2, myemail2@example.com\n into the file in a mode. Now reading the file... \n\n')
for i in ReadCSV(filename, return_type='list'):
    for j in i:
        if j == i[-1]:
            print(j, end='')
        else:
            print(j, end=',')
    print('\n')


print('Done. Bye!')