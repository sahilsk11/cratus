echo "Installing node dependencies..."
cd services/node/;
npm install;
echo "Node dependencies successfuly installed.";

echo "Installing python dependencies...";
cd ../python;
source env/bin/activate;
pip install -r requirements.txt;
deactivate;
echo "Python dependencies successfully installed.";
cd ../..;
