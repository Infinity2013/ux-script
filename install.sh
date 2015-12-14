# install dependencies
sudo apt-get install python-pip python-mysqldb mysql-server
cd utils
sudo python setup.py install
cd ..
cd uiautomator 
sudo python setup.py install
cd ..
if [[ $(grep 'uxsql="MySQLdb"' ~/.bashrc) == "" ]];then
    sed -i '$a/export uxsql="MySQLdb"' ~/.bashrc
fi
echo "---------------------------------------------------------------"
echo "Please run the following cmds under su mode if you behind proxy"
echo "pip install openpyxl BeautifulSoup"
echo "---------------------------------------------------------------"

