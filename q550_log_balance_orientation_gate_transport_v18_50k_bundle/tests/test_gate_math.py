"""Independent algebraic checks on v18.50k gate identities."""
import math,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from gate_math import cancellation,gate_fields

def main():
    random.seed(50)
    largest=0.
    for _ in range(1000):
        b=math.exp(random.uniform(-5,5));c=random.uniform(-.95,.9)
        bprime=random.uniform(-100,100);cprime=random.uniform(-5,5)
        f=gate_fields(b,c,bprime,cprime)
        largest=max(largest,abs(f['cancellation']-cancellation(b,c)))
        s=gate_fields(1/b,c,-bprime/b**2,cprime)
        largest=max(largest,abs(s['cancellation']-f['cancellation']),abs(s['log_gate_rate']-f['log_gate_rate']))
        eps=1e-7/max(1,abs(bprime))
        plus=cancellation(b+eps*bprime,c+eps*cprime)
        minus=cancellation(b-eps*bprime,c-eps*cprime)
        numeric=(plus-minus)/(2*eps)
        if abs(f['c_rate']-numeric)>0.0005:
            raise AssertionError((b,c,bprime,cprime,f['c_rate'],numeric))
        assert f['h']<=1+1e-12
    for c in (-.98,-.75,-.5,0.,.5):
        f=gate_fields(1.,c,123.,-0.01)
        assert f['imbalance_log_cost']==0.
        assert f['log_gate_rate']>0
    print('v18.50k: analytic symmetry, parity-gate, derivative finite differences PASS',largest)
if __name__=='__main__':main()
