#include "fastnmf.h"
#include <vector>
#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

using namespace std;

double dotproduct(int uid,int bid, vector<vector<double> > &P, vector< vector<double > > & Q,int K)
{
  double result = 0;
  for(int i = 0; i < K; i++)
  {
    result += P[uid][i]*Q[bid][i];
  }
  return result;


}

int main(int argc, char **argv)
{
  if(argc != 4)
  {
    printf("Argc is %d\n", argc);
    return 0;
  }
  int N = atoi(argv[1]);
  int M = atoi(argv[2]);
  int K = atoi(argv[3]);


  vector<rating_t> ratings;
  vector<vector< double > > newP;
  for(int i = 0; i < N; i++)
  {
    vector<double> row;
    for(int k = 0; k < K; k++)
    {
      double ran = (double)rand() / (double)(RAND_MAX + 1.0);
      row.push_back(ran);
    }
    newP.push_back(row);
  }

  vector<vector< double > > newQ;
  for(int i = 0; i < N; i++)
  {
    vector<double> row;
    for(int k = 0; k < K; k++)
    {
      double ran = (double)rand() / (double)(RAND_MAX + 1.0);
      row.push_back(ran);
    }
    newQ.push_back(row);
  }

  for(int i = 0; i < N; i++)
  {
    for(int j = 0; j < M; j++)
    {
      double chance = (double)rand() / (double)(RAND_MAX + 1.0);

      if(chance < 0.3)
      {
        rating_t rat;
        rat.uid = i;
        rat.bid = j;
        rat.rat   = dotproduct(i,j,newP, newQ,K);
        ratings.push_back(rat);
      }
    }

  }
  run_nmf_from_c(ratings, N, M, K);

}
