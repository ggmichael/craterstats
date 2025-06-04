
# Gallery

This gallery shows the types of plots produced by Craterstats-III, and the command options used to produce them.
These may be typed on single line following the command `craterstats`, or saved in a file with `.cs` extension
and generate with the command `craterstats -i <filename>.cs`. 

![00-demo](https://ggmichael.github.io/craterstats/demo/00-demo.png)

Demo 0

```
-title "Differential plot with Poisson age evaluations,|equilibrium function, and epoch system"
-cs neukumivanov
-ep mars
-ef trask
-p source=%sample%/Pickering.scc
-p type=poisson,range=[2,5],offset_age=[2,-2]
-p range=[.2,.7]
```

![01-demo](https://ggmichael.github.io/craterstats/demo/01-demo.png)

Demo 1

```
-title Differential plot|with two differential fit age evaluations
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=o
-p type=d-fit,range=[.2,.7],isochron=1
-p range=[2,5],colour=red
```

![02-demo](https://ggmichael.github.io/craterstats/demo/02-demo.png)

Demo 2

```
-title "Differential age fits|with 10/decade binning"
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=o,binning=10/decade
-p type=d-fit,range=[.2,.7],isochron=1
-p range=[2,5],colour=red
```

![03-demo](https://ggmichael.github.io/craterstats/demo/03-demo.png)

Demo 3

```
-title "Cumulative fit|with resurfacing correction"
-pr cumul
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq
```

![04-demo](https://ggmichael.github.io/craterstats/demo/04-demo.png)

Demo 4

```
-title "Cumulative fit with resurfacing correction|showing all corrected data points"
-pr cumul
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq,resurf_showall=1
```

![05-demo](https://ggmichael.github.io/craterstats/demo/05-demo.png)

Demo 5

```
-title "Cumulative fits showing resurfacing correction|and fitted isochrons"
-pr cumul
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[2,5],isochron=1
-p range=[.2,.7],resurf=1,psym=fsq
```

![06-demo](https://ggmichael.github.io/craterstats/demo/06-demo.png)

Demo 6

```
-title "Cumulative fits showing resurfacing correction,|equilibrium function and epoch system"
-pr cumul
-cs neukumivanov
-ep mars
-ef trask
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[2,5]
-p range=[.2,.7],resurf=1,psym=fsq
```

![07-demo](https://ggmichael.github.io/craterstats/demo/07-demo.png)

Demo 7

```
-title "Modified legend 1:|renamed data series, N(1) value but no count or diameter range"
-pr cumul
-cs neukumivanov
-legend fnaN
-p source=%sample%/Pickering.scc,psym=sq,name=Area 1
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq
```

![08-demo](https://ggmichael.github.io/craterstats/demo/08-demo.png)

Demo 8

```
-title "Modified legend 2:|only count and diameter range; no function citations"
-pr cumul
-cs neukumivanov
-legend cr
-p source=%sample%/Pickering.scc,psym=sq,name=Area 1
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq
```

![09-demo](https://ggmichael.github.io/craterstats/demo/09-demo.png)

Demo 9

```
-title R-plot with 10/decade binning
-pr rplot
-cs neukumivanov
-ep mars
-p source=%sample%/Pickering.scc,psym=o,binning=10/decade
-p type=poisson,range=[.2,.7],psym=fo,offset_age=[-9,0]
```

![10-demo](https://ggmichael.github.io/craterstats/demo/10-demo.png)

Demo 10

```
-title Hartmann style plot
-pr hartmann
-cs hartmanndaubar2016
--equilibrium hartmann
-isochrons 4s,3.7s,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
-p source=%sample%/Pickering.scc,binning=root2
```

![11-demo](https://ggmichael.github.io/craterstats/demo/11-demo.png)

Demo 11

```
-title Hartmann-style plot with other binning
-pr hartmann
-cs hart04
-ef hart84
-isochrons 4s,3.7s,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
-p source=%sample%/Pickering.scc
```

![12-demo](https://ggmichael.github.io/craterstats/demo/12-demo.png)

Demo 12

```
-title Hartmann 2010 crater count template
-pr hartmann
-cs hartmann2010
-ef hart84
-isochrons 4,3.5as,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
```

![13-demo](https://ggmichael.github.io/craterstats/demo/13-demo.png)

Demo 13

```
-title "Hartmann-style plot with other chronology system|Poisson age analysis and without $\mu$-notation"
-pr hartmann
-cs neukumivanov
-mu 0
-ef trask
-p source=%sample%/Pickering.scc,psym=*4,isochron=1
-p type=poisson,colour=blue,range=[.2,.7]
-p colour=red,range=[2,5],offset_age=[3,0]
```

![14-demo](https://ggmichael.github.io/craterstats/demo/14-demo.png)

Demo 14

```
-title "Impact rate function|with alternative specified reference diameter"
-pr rate
-ref_diameter 10
-yrange -7 2
```

![15-demo](https://ggmichael.github.io/craterstats/demo/15-demo.png)

Demo 15

```
-title Chronology function with Mars epochs and transition times
-pr chronology
-ep mars
-cs neukumivanov
```

![16-demo](https://ggmichael.github.io/craterstats/demo/16-demo.png)

Demo 16

```
-title Chronology function with lunar epochs and transition times
-pr chronology
-ep wilhelms
```

![17-demo](https://ggmichael.github.io/craterstats/demo/17-demo.png)

Demo 17

```
-title "Poisson calculation for buffered crater count|indicating area and perimeter"
-cs neukum83
-pr diff
-p source=%sample%/c7.scc
-p type=b-poisson,range=[.25,2]
```

![18-demo](https://ggmichael.github.io/craterstats/demo/18-demo.png)

Demo 18

```
-title "Differential plot|with root-2 binning and root-2 diameter scale"
-cs neukumivanov
-style root-2
-p source=%sample%/Pickering.scc,psym=x,binning=root-2
-p type=poisson,range=[.2,.7],isochron=1
-p range=[2,5],colour=violet,offset_age=[2,-3]
```

![19-demo](https://ggmichael.github.io/craterstats/demo/19-demo.png)

Demo 19

```
-title Cumulative plot|with no binning
-pr cumul
-cs neukumivanov
-p source=%sample%/Pickering.scc,binning=none,psym=point
-p type=poisson,colour=red,range=[.22,.43],isochron=1
-p range=[2,5],colour=blue,offset_age=[2,-2]
```

![20-demo](https://ggmichael.github.io/craterstats/demo/20-demo.png)

Demo 20

```
-title Plot with inverted colour
-cs neukumivanov
-invert 1
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7],isochron=1
-p range=[2,5],colour=violet,offset_age=[2,-3]
```

![21-demo](https://ggmichael.github.io/craterstats/demo/21-demo.png)

Demo 21

```
-title Plot with left-positioned age annotation
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7]
-p range=[2,5],colour=blue,age_left=1
```

![22-demo](https://ggmichael.github.io/craterstats/demo/22-demo.png)

Demo 22

```
-title "Plot with adjusted position of age annotation:|offset_age=[+1,+4] (in 1/20ths of decade)""
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7]
-p range=[2,5],colour=blue,age_left=1,offset_age=[1,4]
```

![23-demo](https://ggmichael.github.io/craterstats/demo/23-demo.png)

Demo 23

```
-title Fig 3, Michael et al (2021)
-p src=%sample%/c1.scc,sym=^,err=0
-p src=%sample%/c2.scc,sym=f^,col=grey
-p src=%sample%/c3.scc,sym=s4
-p src=%sample%/c4.scc,sym=o
-p src=%sample%/c5.scc,sym=x
-p src=%sample%/c6.scc,sym=s5,col=pink3
-p src=%sample%/c7.scc,sym=sq
-p src=%sample%/Im2.scc,sym=fo,col=blk,err=1
-p type=poisson,range=[1.8,20],snap=0,offset=[-5,2]
-isochrons .5a,.05a,.005s
-xrange -3 2
-yrange -5 5
-pt_size 9
-sf 2
```

[View the PDF](https://ggmichael.github.io/craterstats/demo/24-demo.svg)

Demo 24

```
-title Plot in SVG vector format
-f svg
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7],isochron=1
-p range=[2,5],colour=blue,offset_age=[2,-3]
```

![25-demo](https://ggmichael.github.io/craterstats/demo/25-demo_age.png)
![25-demo](https://ggmichael.github.io/craterstats/demo/25-demo_err.png)
![25-demo](https://ggmichael.github.io/craterstats/demo/25-demo_k.png)

Demo 25

```
-title "Evaluation of small-area, low-number count|assuming complete count of craters >150 m"
-pr uncertainty
-cs n83
-ef trask
-d_min 0.15
```

![26-demo](https://ggmichael.github.io/craterstats/demo/26-demo.png)

Demo 26

```
-title Sequence plot
-pr seq
-cs n83
-ep moon
-xrange 4.0 1
-legend fA
-p src=%sample%/e1.diam,range=[0.24,1.5],name=E1,type=poisson,snap=0
-p src=%sample%/e2.diam,rng=[0.25,1.5],nm=E2
-p src=%sample%/e3.diam,rng=[0.24,1.5],nm=E3
-p src=%sample%/w1.diam,rng=[0.21,1.2],colour=red,nm=W1
-p src=%sample%/w2.diam,rng=[0.18,1],nm=W2
-p src=%sample%/w2.diam,rng=[1.5,5],nm=W2
-p src=%sample%/w2_h.diam,rng=[0.16,0.6],nm=W2h
-p src=%sample%/w2_h.diam,rng=[0.8,1.9],nm=W2h
-p src=%sample%/w2_l.diam,rng=[0.19,1.1],nm=W2l
-p src=%sample%/w3.diam,rng=[0.16,1.5],colour=red1,nm=W3
-p src=%sample%/w4.diam,rng=[0.185,1.55],nm=W4
-p src=%sample%/w5_h1.diam,rng=[0.17,1],colour=blue,nm=W5h1
-p src=%sample%/w5_h2.diam,rng=[0.13,1.35],nm=W5h2
-p src=%sample%/w5_h3.diam,rng=[0.14,0.85],nm=W5h3
-p src=%sample%/w5_l1.diam,rng=[0.165,0.85],colour=blue2,nm=W5l1
-p src=%sample%/w5_l2.diam,rng=[0.12,0.8],nm=W5l2
-p src=%sample%/w5_l3.diam,rng=[0.15,0.8],nm=W5l3
```

![27-demo](https://ggmichael.github.io/craterstats/demo/27-demo.png)

Demo 27

```
-title "Bin overlay to aid diameter selection|(normally remove before publication)""
-cs neukumivanov
-p source=%sample%/Pickering.scc,binning=pseudo-log
-p type=poisson,range=[.26,.63]
--bins
```
