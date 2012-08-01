PYTHON= /usr/include/python2.7

BOOST_INC= /Users/zouf/pool/include
BOOST_LIB= /Users/zouf/pool/lib

OBJ= fastnmf

ALL= fastnmf.so driver

all: $(ALL)


driver: driver.o fastnmf.o
	g++  -O3 -dynamic driver.o fastnmf.o -L$(BOOST_LIB) \
	-lboost_python -L/usr/lib/python2.7/config \
	-lpython2.7 -o driver

driver.o:
	g++   -O3 -I$(PYTHON) -I$(BOOST_INC) -c -fPIC driver.cpp -o driver.o


fastnmf.so: fastnmf.o
	g++   -shared -O3 -dynamic  \
	g++ -O3 -I$(PYTHON) -I$(BOOST_INC) -c -fPIC driver.cpp -o driver.o


fastnmf.so: fastnmf.o
	g++  -shared -O3 -dynamic  \
	fastnmf.o -L$(BOOST_LIB) -lboost_python \
	-L/usr/lib/python2.7/config -lpython2.7 \
	-o fastnmf.so


fastnmf.o: fastnmf.cpp
	g++  -O3 -I$(PYTHON) -I$(BOOST_INC) -c -fPIC fastnmf.cpp -o fastnmf.o

clean:
	rm -f *.o  driver *.so
