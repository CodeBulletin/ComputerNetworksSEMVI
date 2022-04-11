# include <iostream>
#include <cmath>
using namespace std;

# define TOT_FRAMES 500
# define FRAMES_SEND 10

class gobkn
{
 private:
  int fr_send_at_instance;
  int arr[TOT_FRAMES];
  int arr1[FRAMES_SEND];
  int sw;
  int rw; // tells expected frame
 public:
  gobkn();
  void input();
  void sender(int);
  void reciever(int);
};

gobkn :: gobkn()
{
 sw = 0;
 rw = 0;
}

void gobkn :: input()
{
 int n;  // no of bits for the frame
 int m;  // no of frames from n bits

 cout << "Enter the no of bits for the sequence no ";
 cin >> n;

 m = pow (2 , n);

 int t = 0;

 fr_send_at_instance = (m / 2);

 for (int i = 0 ; i < TOT_FRAMES ; i++)
 {
  arr[i] = t;
  t = (t + 1) % m;
 }

 sender(m);
}

void gobkn :: sender(int m)
{
 int j = 0;

 for (int i = sw ; i < sw + fr_send_at_instance ; i++)
 {
  arr1[j] = arr[i];
  j++;
 }

 for (int i = 0 ; i < j ; i++)
  cout << " SENDER   : Frame " << arr1[i] << " is sent\n";

 reciever (m);
}

void gobkn :: reciever(int m)
{
 time_t t;
 int f;
 int f1;
 int a1;
 char ch;

 srand((unsigned) time(&t));
 f = rand() % 10;

   // if = 5 frame is discarded for some reason
   // else they are correctly recieved

 if (f != 5)
 {
  for (int i = 0 ; i < fr_send_at_instance ; i++)
  {
   if (rw == arr1[i])
   {
    cout << "RECIEVER : Frame " << arr1[i] << " recieved correctly\n";
    rw = (rw + 1) % m;
   }
   else
    cout << "RECIEVER : Duplicate frame " << arr1[i] << " discarded\n";
  }
  a1 = rand() % 15;

   // if a1 belongs to 0 to 3 then
   //     all ack after this (incl this one) lost
   // else
   //     all recieved

  if (a1 >= 0 && a1 <= 3)
  {
   cout << "(Acknowledgement " << arr1[a1] << " & all after this lost)\n";
   sw = arr1[a1];
  }
  else
   sw = (sw + fr_send_at_instance) % m;
 }
 else
 {
  f1 = rand() % fr_send_at_instance;

   // f1 gives index of the frame being lost

  for (int i = 0 ; i < f1 ; i++)
  {
   if (rw == arr1[i])
   {
    cout << " RECIEVER : Frame " << arr1[i] << " recieved correctly\n";
    rw = (rw + 1) % m;
   }
   else
    cout << " RECIEVER : Duplicate frame " << arr1[i] << " discarded\n";
  }

  int ld = rand() % 2;
    // ld == 0 frame damaged
    // else frame lost
  if (ld == 0)
   cout << " RECIEVER : Frame " << arr1[f1] << " damaged\n";
  else
   cout << "            (Frame " << arr1[f1] << " lost)\n";

  for (int i = f1 + 1 ; i < fr_send_at_instance ; i++)
    cout << " RECIEVER : Frame " << arr1[i] << " discarded\n";

  cout << " (SENDER TIMEOUTS --> RESEND THE FRAME)\n";

  sw = arr1[f1];
 }
 cout << "Want to continue...";
 cin >> ch;

 if (ch == 'y')
  sender(m);
 else
  exit(0);
}

int main()
{

 gobkn gb;
 gb.input();

}