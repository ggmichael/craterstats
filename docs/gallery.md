
# Gallery

![00-demo](demo\00-demo.png)

Demo 0

```
-cs neukumivanov
-ep mars
-ef trask
-title Differential plot with Poisson age evaluations,|equilibrium function, and epoch system
-p source=%sample%/Pickering.scc
-p type=poisson,range=[2,5],offset_age=[2,-2]
-p range=[.2,.7]
```

![01-demo](demo\01-demo.png)

Demo 1

```
-cs neukumivanov
-title Differential plot|with two differential fit age evaluations
-p source=%sample%/Pickering.scc,psym=o
-p type=d-fit,range=[.2,.7],isochron=1
-p range=[2,5],colour=red
```

![02-demo](demo\02-demo.png)

Demo 2

```
-cs neukumivanov
-title Differential age fits|with 10/decade binning
-p source=%sample%/Pickering.scc,psym=o,binning=10/decade
-p type=d-fit,range=[.2,.7],isochron=1
-p range=[2,5],colour=red
```

![03-demo](demo\03-demo.png)

Demo 3

```
-pr cumul
-title Cumulative fit|with resurfacing correction
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq
```

![04-demo](demo\04-demo.png)

Demo 4

```
-pr cumul
-cs neukumivanov
-title Cumulative fit with resurfacing correction|showing all corrected data points
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq,resurf_showall=1
```

![05-demo](demo\05-demo.png)

Demo 5

```
-pr cumul
-cs neukumivanov
-title Cumulative fits showing resurfacing correction|and fitted isochrons
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[2,5],isochron=1
-p range=[.2,.7],resurf=1,psym=fsq
```

![06-demo](demo\06-demo.png)

Demo 6

```
-pr cumul
-cs neukumivanov
-ep mars
-ef trask
-title Cumulative fits showing resurfacing correction,|equilibrium function and epoch system
-p source=%sample%/Pickering.scc,psym=sq
-p type=c-fit,range=[2,5]
-p range=[.2,.7],resurf=1,psym=fsq
```

![07-demo](demo\07-demo.png)

Demo 7

```
-pr cumul
-cs neukumivanov
-legend fnaN
-title Modified legend 1:|renamed data series, N(1) value but no count or diameter range
-p source=%sample%/Pickering.scc,psym=sq,name=Area 1
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq
```

![08-demo](demo\08-demo.png)

Demo 8

```
-pr cumul
-cs neukumivanov
-legend cr
-title Modified legend 2:|only count and diameter range; no function citations
-p source=%sample%/Pickering.scc,psym=sq,name=Area 1
-p type=c-fit,range=[.2,.7],resurf=1,psym=fsq
```

![09-demo](demo\09-demo.png)

Demo 9

```
-pr rplot
-cs neukumivanov
-ep mars
-title R-plot|with 10/decade binning
-p source=%sample%/Pickering.scc,psym=o,binning=10/decade
-p type=poisson,range=[.2,.7],psym=fo,offset_age=[-9,0]
```

![10-demo](demo\10-demo.png)

Demo 10

```
-pr hartmann
-cs hart04
-ef hart84
-title Hartmann-style plot|with specified isochrons
-isochrons 4s,3.7s,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
-p source=%sample%/Pickering.scc,psym=o
```

![11-demo](demo\11-demo.png)

Demo 11

```
-pr hartmann
-cs h&d2016
--equilibrium hartmann
-title Hartmann style plot|with H&D 2016 production function
-isochrons 4s,3.7s,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
-p source=%sample%/Pickering.scc,psym=o
```

![12-demo](demo\12-demo.png)

Demo 12

```
-pr hartmann
-cs hartmann2010
-ef hart84
-isochrons 4s,3.5as,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
-title Hartmann 2010 crater count template
```

![13-demo](demo\13-demo.png)

Demo 13

```
-pr hartmann
-cs neukumivanov
-mu 0
-ef trask
-title Hartmann-style plot with other chronology system|Poisson age analysis and without $\mu$-notation
-p source=%sample%/Pickering.scc,psym=*4,isochron=1
-p type=poisson,colour=blue,range=[.2,.7]
-p colour=red,range=[2,5],offset_age=[3,0]
```

![14-demo](demo\14-demo.png)

Demo 14

```
-pr rate
-ref_diameter 10
-yrange -7 2
-title Impact rate function|with alternative specified reference diameter
```

![15-demo](demo\15-demo.png)

Demo 15

```
-pr chronology
-ep mars
-cs neukumivanov
-title Chronology function|with Mars epochs and transition times
```

![16-demo](demo\16-demo.png)

Demo 16

```
-pr chronology
-ep wilhelms
-title Chronology function|with lunar epochs and transition times
```

![17-demo](demo\17-demo.png)

Demo 17

```
-title Poisson calculation for buffered crater count|indicating area and perimeter
-cs neukum83
-pr diff
-p source=%sample%/c7_Michael-et-al-2021.scc,name=c7
-p type=b-poisson,range=[.25,2]
```

![18-demo](demo\18-demo.png)

Demo 18

```
-cs neukumivanov
-style root-2
-title Differential plot|with root-2 binning and root-2 diameter scale
-p source=%sample%/Pickering.scc,psym=x,binning=root-2
-p type=poisson,range=[.2,.7],isochron=1
-p range=[2,5],colour=violet,offset_age=[2,-3]
```

![19-demo](demo\19-demo.png)

Demo 19

```
-pr cumul
-cs neukumivanov
-title Cumulative plot|with no binning
-p source=%sample%/Pickering.scc,binning=none,psym=point
-p type=poisson,colour=red,range=[.22,.43],isochron=1
-p range=[2,5],colour=blue,offset_age=[2,-2]
```

![20-demo](demo\20-demo.png)

Demo 20

```
-cs neukumivanov
-invert 1
-title Plot with inverted colour
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7],isochron=1
-p range=[2,5],colour=violet,offset_age=[2,-3]
```

![21-demo](demo\21-demo.png)

Demo 21

```
-cs neukumivanov
-title Plot with left-positioned age annotation
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7]
-p range=[2,5],colour=blue,age_left=1
```

![22-demo](demo\22-demo.png)

Demo 22

```
-cs neukumivanov
-title Plot with adjusted position of age annotation:|offset_age=[+1,+4] (in 1/20ths of decade)
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7]
-p range=[2,5],colour=blue,age_left=1,offset_age=[1,4]
```

[View the PDF](demo\23-demo.pdf)

Demo 23

```
-f pdf
-cs neukumivanov
-title Plot in PDF format
-p source=%sample%/Pickering.scc,psym=fo
-p type=poisson,range=[.2,.7],isochron=1
-p range=[2,5],colour=blue,offset_age=[2,-3]
```

![24-demo](demo\24-demo_age.png)
![24-demo](demo\24-demo_err.png)
![24-demo](demo\24-demo_k.png)

Demo 24

```
-pr uncertainty
-cs n83
-ef trask
-d_min 0.15
-title Evaluation of small-area, low-number count|assuming complete count of craters >150 m
```

![25-demo](demo\25-demo.png)

Demo 25

```
--bins
-cs neukumivanov
-title Bin overlay to aid diameter selection|(normally remove before publication)
-p source=%sample%/Pickering.scc,binning=pseudo-log
-p type=poisson,range=[.26,.63]
```
