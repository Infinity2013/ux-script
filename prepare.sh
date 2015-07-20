current=$(pwd)
for push in $(find -name "push.sh")
do
	tmp=$(dirname $push)
	cd $tmp
	./push.sh
	cd $current
done
