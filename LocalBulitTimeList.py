import calendar

def LocalBulitTimeList(start_time_year, start_time_month, start_time_day, end_time_year ,end_time_month, end_time_day):
    temp_mouth_dict = dict()
    time_list = list()

    # 将需要还原的变量值入栈
    Stack = list()
    Stack.append(start_time_year)
    Stack.append(start_time_month)

    while True:
        if start_time_year == end_time_year and start_time_month == end_time_month + 1:
            break     

        temp_mouth_dict[str(f"{start_time_year}-{start_time_month}")] = calendar.monthrange(start_time_year, start_time_month)[1]

        if start_time_month == 12:  
            if start_time_year != end_time_year:
                start_time_year += 1
            start_time_month = 1
        else:
            start_time_month += 1

    # 将需要还原的变量值出栈，进行还原
    start_time_year = Stack[0]
    start_time_month = Stack[1]
    
    for i in list(temp_mouth_dict.keys()):
        for a in range(temp_mouth_dict[i]):
            if int(i.split("-")[0]) == end_time_year and int(i.split("-")[1]) == end_time_month:
                
                if int(start_time_day) == int(end_time_day):
                    if len(start_time_day) == 1:
                        if len(start_time_month) == 1:
                            time_list.append(str(end_time_year) + "-0" + str(start_time_month) + "-0" + str(end_time_day))
                        else:
                            time_list.append(str(end_time_year) + "-" + str(start_time_month) + "-0" + str(end_time_day))
                    else:
                        if len(start_time_month) == 1:
                            time_list.append(str(end_time_year) + "-0" + str(start_time_month) + "-" + str(end_time_day))
                        else:
                            time_list.append(str(end_time_year) + "-" + str(start_time_month) + "-" + str(end_time_day))
                    break

                if a + 1 > int(end_time_day):
                    break
                else:
                    if a < 9:
                        if len(str(i.split("-")[1])) == 2:
                            time_list.append(str(i) + "-0" + str(a + 1))
                        else:
                            time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-0" + str(a + 1))
                    else:
                        if len(str(i.split("-")[1])) == 2:
                            time_list.append(str(i) + "-" + str(a + 1))
                        else:
                            time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-" + str(a + 1))
            
            elif int(i.split("-")[0]) == start_time_year and int(i.split("-")[1]) == start_time_month:
                if a + 1 < int(start_time_day):
                    pass
                else:
                    if a < 9:
                        if len(str(i.split("-")[1])) == 2:
                            time_list.append(str(i) + "-0" + str(a + 1))
                        else:
                            time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-0" + str(a + 1))
                    else:
                        if len(str(i.split("-")[1])) == 2:
                            time_list.append(str(i) + "-" + str(a + 1))
                        else:
                            time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-" + str(a + 1))
            
            else:
                if a < 9:
                    if len(str(i.split("-")[1])) == 2:
                        time_list.append(str(i) + "-0" + str(a + 1))
                    else:
                        time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-0" + str(a + 1))
                else:
                    if len(str(i.split("-")[1])) == 2:
                        time_list.append(str(i) + "-" + str(a + 1))
                    else:
                        time_list.append(str(i.split("-")[0]) + "-0" + str(i.split("-")[1]) + "-" + str(a + 1))
    
    return time_list