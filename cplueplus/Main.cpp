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



void numOfChar(char *t){
	int count[256]={0};
	int len=0;
	while(*t!='\0'){
		count[*t++]++;
		len++;
	}
	int i=0;
	t=t-len;
	while (*t!='\0')
	{
		cout<<*t<<":"<<count[*t]<<endl;
		t++;
	}
}


int myStrlen(const char *str){
	if(str==NULL){
		return 0;
	}
//count<<"tag"'<<endl;
	int len=0;
	while((*str++)!='\0'){
		len++;

	}
	return len;
}

//my_strcp ×Ö·û´®¸´ÖÆ
char *my_strcp(char *dest1,char *src1){
	if(NULL==dest1||NULL==src1)
		return NULL; //throw "Invalid argument(s)"
	while((*dest1++=*src1++)!='\0'){

	}
	return dest1;
}
//my_aoti
//my_itoa
//my_strcmp

int main(){
	char  *dest1;
	char  *src1="hello"	;
	my_strcp(dest1,src1);
	cout<<dest1<<endl;
	system("pause");
	return 0;
}