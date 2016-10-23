for i in `seq 1 100`; do
	useradd -c "Hans Tester$i" -d /home/tester$i tester$i
	echo "tester$i" |passwd  tester$i --stdin
done

