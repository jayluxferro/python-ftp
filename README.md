### A Simple Python FTP Implementation (Just for Illustration)

1. Start **Server** by running.
```
python server.py
```

2. Client Usage<br/>
```
python client.py [server_address] [directory] [concurrent_connections - default is 1]
```

#### Test Example
1. Generate dummy data files
```
./gen_dummy_file
```

2. Run sample test
```
python client.py 127.0.0.1:5000 dummy 3
```
