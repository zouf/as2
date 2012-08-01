#include <boost/python.hpp>
#include <iostream>
#include <string>
#include <stdlib.h>
#include <vector>
#include <stdio.h>
#include <pthread.h>
#include "fastnmf.h"

#undef DEBUG
//#define DEBUG


struct args_t
{
	int uid;
	int bid;
	int k;
	double eij;
};

using namespace std;
using namespace boost::python;

static  int steps = 20000;
static double alpha = 0;
//static double beta = 0.00001;
static double beta = 0.02;
double threshold = 0.1;
static int K = 0;
static int N = 0;
static int M = 0;


static double really_small_num = 0.00000001;

vector<rating_t> allRatings;
vector<vector<double> > P;
vector<vector<double> > Q;




inline double dot_prod(int uid, int bid)
{
	double result = 0;
	for(int i = 0; i < K; i++)
	{
    double tmp = P[uid][i]*Q[bid][i];
     if(tmp > 5.0)
    {
      tmp = 5.0;
    }
    else if (tmp < -5.0)
      tmp = -5.0;
		result += tmp;
	}
	return result;
}

void initialize_p_q()
{
	#ifdef DEBUG
	printf("Initialize P and Q!\n");
	#endif
	srand ( 666 );
	for(int i = 0; i < N; i++)
	{
		vector<double> tmp;
		for(int k = 0; k < K; ++k)
		{
			double r = (double)((double)rand() / (double)(RAND_MAX + 1.0));
			tmp.push_back(r);
		}
		P.push_back(tmp);
	}

	for(int i = 0; i < M; i++)
	{
		vector<double> tmp;
		for(int k = 0; k < K; ++k)
		{
			double r = (double)((double)rand() / (double)(RAND_MAX + 1.0));
			tmp.push_back(r);
		}
		Q.push_back(tmp);
	}
	#ifdef DEBUG
	printf("Done with intialize P and Q!\n");
	#endif
}

void * calc_p_q(void *param)
{
	args_t * args = (args_t *)(param);
	int uid = args->uid;
	int bid = args->bid;
	int k = args->k;
	double eij = args->eij;
	P[uid][k] = P[uid][k] + alpha * (eij * Q[bid][k] - beta * P[uid][k]);

	Q[bid][k] = Q[bid][k] + alpha * (eij * P[uid][k] - beta * Q[bid][k]);
}


void extractList(list & ratings)
{
  for(int i = 0; i < len(ratings); ++i)
	{
		rating_t r;
		list rating = extract<list>(ratings[i]);
		r.uid = (int)extract<int>(rating[0]);
		r.bid = (int)extract<int>(rating[1]);
		r.rat = (double)extract<float>(rating[2]);
    allRatings.push_back(r);
	}
}


void run_nmf_from_c(vector<rating_t>  ratings, int p_N, int p_M, int p_K)
{
  K = p_K;
  N = p_N;
  M = p_M;
  allRatings.clear();
  P.clear();
  Q.clear();

	alpha = 0.0035;
	steps = 20000;

  allRatings = ratings;
	initialize_p_q();
  run_nmf_c();


}


void run_nmf_from_python(list& ratings, int p_N, int p_M, int p_K, int p_Steps, double p_Alpha, list& p_P, list &p_Q)
{
  K = p_K;
  N = p_N;
  M = p_M;
  alpha = p_Alpha;
  steps = p_Steps;
  allRatings.clear();
  P.clear();
  Q.clear();
#ifdef DEBUG
  printf("run_nmf_from_python with N=%d M=%d K=%d\n",N,M,K);
#endif
  extractList(ratings);
  initialize_p_q();
  run_nmf_c();
  for(int i = 0; i < N; ++i)
  {
    list tmp;
    for(int k = 0; k < K; ++k)
    {
      tmp.append(P[i][k]);
    }
    p_P.append(tmp);
  }
  for(int i = 0; i < M; ++i)
  {
    list tmp;
    for(int k = 0; k < K; ++k)
    {
      tmp.append(Q[i][k]);
    }
    p_Q.append(tmp);
  }

  return;

}


static double prev_e = 0;

void run_nmf_c()
{
	prev_e = 0;
	int numRatings = allRatings.size();
	#ifdef DEBUG
	printf("run_nmf_c with N=%d M=%d K=%d numRatings=%d\n",N,M,K,numRatings);
  printf("\talpha=%lf, beta=%lf,steps = %d\n", alpha,beta,steps);
	#endif

	double thresh_met = 0;
	for(int s = 0; s < steps; ++s)
	{
		for(int r = 0; r < numRatings; ++r)
		{
			int uid = allRatings[r].uid;
			int bid = allRatings[r].bid;
			double rat = allRatings[r].rat;
      double dp = dot_prod(uid,bid);
			double eij = (double)rat - dp;
			for(int k = 0; k < K; ++k)
      {
        double uv = P[uid][k];
        P[uid][k] +=  alpha * (eij * Q[bid][k] - beta * P[uid][k]);
        Q[bid][k] +=  alpha * (eij * uv - beta * Q[bid][k]);
      }
		}
		double e = 0;
		for(int r = 0; r < numRatings; ++r)
		{

			int uid = allRatings[r].uid;
			int bid = allRatings[r].bid;
			double rat = allRatings[r].rat;
			double eij = (double)rat - dot_prod(uid,bid);
			e = e + eij*eij;
			for(int k = 0; k < K; ++k)
			{
				e = e + (beta/2)* (P[uid][k]*P[uid][k] + Q[bid][k]*Q[bid][k]);
			}
		}
    if(e > prev_e && prev_e != 0)
    {
      //alpha = alpha - 0.002;
		   //alpha = alpha * 0.95;
      #ifdef DEBUG
     // printf("Changing alpha to %lf\n",alpha);
      #endif
    }
    prev_e = e;
    //e = e / numRatings;

	  #ifdef DEBUG
    if(s %100 == 0)
		{
			printf("Step s = %d e = %lf!\n",s, e);
		}
		#endif
		if(e < threshold)
		{
			printf("Reached threshold at step = %d\n", s);
			thresh_met = 0;
			break;
		}
		thresh_met = e;
	}
	if(thresh_met)
	{
		printf("Did not reach threshold and %d steps. Got to %lf\n", steps, thresh_met);
	}

	return;
}


using namespace boost::python;

BOOST_PYTHON_MODULE(fastnmf)
{
    def("run_nmf_from_python", run_nmf_from_python, "Runs NMF in C");
}
