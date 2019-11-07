echo "Installing system dependencies..."
echo "Root permission required to install PostgreSQL"
sudo apt install postgresql
sudo apt install python3-venv
echo "Installing node dependencies..."
cd services/node/;
npm install;
echo "Node dependencies successfuly installed.";

echo "Installing python dependencies...";
cd ../python;
python3 -m venv ./env
source env/bin/activate;
pip install -r requirements.txt;
deactivate;
echo "Python dependencies successfully installed.";
cd ../..;
