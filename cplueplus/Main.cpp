#include <iostream>

using namespace std;

template <class T,class N>
T sum(T a,N b ){
	return a+b;
}
namespace myname{
	int x=15;
}

void pointAndArrays(void){
	cout<<"------------------------------"<<endl;
	int arrays[5];
	int *p;
	p=arrays;
	*p=10;
	p++;
	*p=12;
	p--;
	cout<<*p++<<endl;
	p--;
	arrays[2]=1;
	for(int i=0;i<5;i++){
		cout<<*p<<endl;
		p++;
	}

}
int main(){
	int a(12);
	cout<<sum(10,1)<<endl;
	cout<<myname::x<<endl;
	cout<<a<<endl;
	pointAndArrays();
	system("pause");
	return 0;
}