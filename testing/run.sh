for i in {1..10}
do
    echo "Client $i started with PID: $pid"
    python3 client3.py > outcome{$i}.txt &
done