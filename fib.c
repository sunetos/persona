#include <math.h>

struct Point {
  float x;
  float y;
};

float distance(struct Point *p1, struct Point* p2) {
  return sqrt((p1->x - p2->x)*(p1->x - p2->x) +
              (p1->y - p2->y)*(p1->y - p2->y));
}

int fib(int n) {
  if (n < 3) {
   return 1;
  } else {
   return fib(n-1) + fib(n-2);
  }
}

struct Vec3 {
  float x;
  float y;
  float z;
};

struct LotsOfStuff {
  int ReallyLongName1;
  int ReallyLongName2;
  int ReallyLongName3;
  int ReallyLongName4;
  int ReallyLongName5;
  int ReallyLongName6;
};
