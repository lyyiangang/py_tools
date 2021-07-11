#!/bin/bash
tag='<none>'
for line in $(docker images | awk '{print $1$3}')
do
    # 包含none的行要删除,注意下面的空格不能丢．．．．
    if [[ $line =~ $tag ]]
    then
        img_id=$(echo $line | sed 's/<none>//')
        echo deleting image $img_id
        docker image rm $img_id
    fi
done

echo 'after removing operation, the left images as below'
docker images

