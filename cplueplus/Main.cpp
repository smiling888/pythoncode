#include <iostream>
#define getmax1(a,b) ((a)>(b)?(a):(b))
using namespace std;

template <class T,class N>
T sum(T a,N b ){
	return a+b;
}
namespace myname{
	int x=15;
}

class ThisTest{

public:
	bool  isitme(ThisTest &th){
		if(&th==this){
			return true;
		}
		return false;
	}
};


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


//class template
template <class T>
class mypair{
	T a,b;
public:
	mypair(T first,T second){
		a=first;
		b=second;
	}
	T getmax();
};

template <class T>
T mypair<T>::getmax(){
	
	return a>b?a:b;
	
}

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

	cout<<"thistest----------"<<endl;
	ThisTest ta;
	ThisTest *tb=&ta;
	if(tb->isitme(ta))
		cout<<"yes it is me"<<endl;
	
	cout<<getmax1(2,5)<<endl;
	system("pause");
	return 0;
}