import re,math; 
def lab_to_hex(L,a,b):
    fy=(L+16)/116; fx=fy+a/500; fz=fy-b/200
    def f_inv(t): return t**3 if t**3>0.008856 else (t-16/116)/7.787
    xr=f_inv(fx); yr=f_inv(fy); zr=f_inv(fz)
    X=95.047*xr; Y=100*yr; Z=108.883*zr
    x=X/100; y=Y/100; z=Z/100
    r= 3.2406*x -1.5372*y -0.4986*z
    g=-0.9689*x +1.8758*y +0.0415*z
    b= 0.0557*x -0.2040*y +1.0570*z
    def comp(c):
        c=0 if c<0 else (1 if c>1 else c)
        return 12.92*c if c<=0.0031308 else 1.055*(c**(1/2.4))-0.055
    r=comp(r); g=comp(g); b=comp(b)
    return f"#{int(round(r*255)):02X}{int(round(g*255)):02X}{int(round(b*255)):02X}"
with open(r"c:\Users\wesse\Documents\code\hitster\tmp.txt") as f: 
    for line in f:
        m=re.match(r"(\S+):\s*lab\(([^%]+)%\s*([-\d.]+)\s*([-\d.]+)\)", line.strip())
        if not m: continue
        name,L,a,b=m.group(1),float(m.group(2)),float(m.group(3)),float(m.group(4))
        print(f"{name}: {lab_to_hex(L,a,b)}")