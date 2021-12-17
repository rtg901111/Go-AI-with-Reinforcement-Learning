def read_input(file_name: str):

    line_count = 0

    previous_board = []

    current_board = []

    file = open(file_name, 'r')

    n_count = 0

    for line in file:  
        if line_count == 0:
            stone_type = int(line)
        
        elif line_count > 0 and line_count < 6:
            temp_list = []
            for num in line.rstrip('\n'):
                temp_list.append(int(num))
            previous_board.append(temp_list)

        elif line_count > 5: 
            temp_list = []
            for num in line.rstrip('\n'):
                temp_list.append(int(num))
                if int(num) != 0:
                    n_count += 1
    
            current_board.append(temp_list)
        
        line_count += 1

    return stone_type, previous_board, current_board, n_count

def write_output(file_name, action):
    file = open(file_name, 'w')
    if action == 'PASS':
        file.write('PASS')
    else:
        file.write(str(action[0]) + ',' + str(action[1]))

    file.close()
    
 