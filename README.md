Async proxy server
-Https, http requests
-async
-users-auth
-blocking domains

Usage:

1) Ussual mode, blocks base sites (you can see it in console)
python main.py 

2) File mode. Blocks base sites + domains obtained from the file
python main.py -f "file_path"

3) Arguments mode. Blocks base sites + domains obtained from the arguments
python main.py -a "domain_to_block_1" "domain_to_block_N"

4) File mode + Arguments mode. Blocks base sites + domains obtained from the arguments + domains obtained from the file
python main.py -a "domain_to_block_1" "domain_to_block_N" -f "file_path"




