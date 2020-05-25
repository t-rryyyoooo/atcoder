#!/bin/bash

language=$1
tasks=(task_*.txt)
answers=(ans_*.txt)
length=${#tasks[@]}

cnt=1
check=0

for x in `seq 0 $(($length - 1))`
do
 printf "Sample${cnt} : "


 diff <($language solve.py < ${tasks[$x]}) <(cat ${answers[$x]}) --brief > /dev/null

 if [ $? -eq 0 ];then
  printf "\e[32mAC\n\e[m" 

 else
  let check++

  printf "\e[31mWA\n\e[m"

  printf "\e[31mPredicted\n"
  $language solve.py < ${tasks[$x]} | printf "$(cat)\n"

  printf "Result\n"
  cat ${answers[$x]} | printf "$(cat)\n\e[m"

 fi

 printf "\e[m"

 let cnt++

done

if [ $check -eq 0 ];then
 python3 submit.py -l $language

fi

