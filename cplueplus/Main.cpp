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
// º¯ÊýÖ¸Õë
int add(int a, int b){
return a+b;

}
int op(int a, int b, int (*fun)(int ,int)){
  return fun(a,b);
}
struct fruit{
	float weight;
	double price;
}apple,banana,melon;

int main(){
	int a(12);
	cout<<sum(10,1)<<endl;
	cout<<myname::x<<endl;
	cout<<a<<endl;
	pointAndArrays();
	cout<<op(1,2,add);
	apple.weight=10.0;
	apple.price=20.0;
cout<<apple.price<<endl;
	system("pause");
	return 0;
}