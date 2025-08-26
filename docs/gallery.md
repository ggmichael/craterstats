  
# Gallery

This gallery shows the types of plots produced by Craterstats-III, and the command options used to produce them.
These may be typed on single line following the command `craterstats`, or saved in a file with `.cs` extension
and generated with the command `craterstats -i <filename>.cs`. 

![00-demo](https://ggmichael.github.io/craterstats/demo/00-demo.png)

Demo 0

```
-title 'Differential plot with Poisson age evaluations,|equilibrium function, and epoch system'
-cs neukumivanov
-ep mars
-ef trask
-p source=%sample%/Pickering.scc
-p 'type=poisson,range=[2,5],offset_age=[2,-2]'
-p 'range=[.2,.7]'
```

![01-demo](https://ggmichael.github.io/craterstats/demo/01-demo.png)

Demo 1

```
-title Differential 'plot|with' two differential fit age evaluations
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=o
-p 'type=d-fit,range=[.2,.7],isochron=1'
-p 'range=[2,5],colour=red'
```

![02-demo](https://ggmichael.github.io/craterstats/demo/02-demo.png)

Demo 2

```
-title 'Differential age fits|with 10/decade binning'
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=o,binning=10/decade
-p 'type=d-fit,range=[.2,.7],isochron=1'
-p 'range=[2,5],colour=red'
```

![03-demo](https://ggmichael.github.io/craterstats/demo/03-demo.png)

Demo 3

```
-title 'Cumulative fit|with resurfacing correction'
-pr cumul
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=sq
-p 'type=c-fit,range=[.2,.7],resurf=1,psym=fsq'
```

![04-demo](https://ggmichael.github.io/craterstats/demo/04-demo.png)

Demo 4

```
-title 'Cumulative fits showing resurfacing correction|and fitted isochrons'
-pr cumul
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=sq
-p 'type=c-fit,range=[2,5],isochron=1'
-p 'range=[.2,.7],resurf=1,psym=fsq'
```

![05-demo](https://ggmichael.github.io/craterstats/demo/05-demo.png)

Demo 5

```
-title 'Cumulative fits showing resurfacing correction,|equilibrium function and epoch system'
-pr cumul
-cs neukumivanov
-ep mars
-ef trask
-p source=%sample%/Pickering.scc,psym=sq
-p 'type=c-fit,range=[2,5]'
-p 'range=[.2,.7],resurf=1,psym=fsq'
```

![06-demo](https://ggmichael.github.io/craterstats/demo/06-demo.png)

Demo 6

```
-title 'Modified legend 1:|renamed data series, N(1) value but no count or diameter range'
-pr cumul
-cs neukumivanov
-legend fnaN
-p source=%sample%/Pickering.scc,psym=sq,name=Area 1
-p 'type=c-fit,range=[.2,.7],resurf=1,psym=fsq'
```

![07-demo](https://ggmichael.github.io/craterstats/demo/07-demo.png)

Demo 7

```
-title 'Modified legend 2:|only count and diameter range; no function citations'
-pr cumul
-cs neukumivanov
-legend cr
-p source=%sample%/Pickering.scc,psym=sq,name=Area 1
-p 'type=c-fit,range=[.2,.7],resurf=1,psym=fsq'
```

![08-demo](https://ggmichael.github.io/craterstats/demo/08-demo.png)

Demo 8

```
-title R-plot with 10/decade binning
-pr rplot
-cs neukumivanov
-ep mars
-p source=%sample%/Pickering.scc,psym=o,binning=10/decade
-p 'type=poisson,range=[.2,.7],psym=fo,offset_age=[-9,0]'
```

![09-demo](https://ggmichael.github.io/craterstats/demo/09-demo.png)

Demo 9

```
-title Hartmann style plot
-pr hartmann
-cs hartmanndaubar2016
--equilibrium hartmann
-isochrons 4s,3.7s,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
-p source=%sample%/Pickering.scc,binning=root2
```

![10-demo](https://ggmichael.github.io/craterstats/demo/10-demo.png)

Demo 10

```
-title Hartmann-style plot with finer binning
-pr hartmann
-cs hart04
-ef hart84
-isochrons 4s,3.7s,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
-p source=%sample%/Pickering.scc
```

![11-demo](https://ggmichael.github.io/craterstats/demo/11-demo.png)

Demo 11

```
-title Hartmann 2010 crater count template
-pr hartmann
-cs hartmann2010
-ef hart84
-isochrons 4,3.5as,3s,1,.1,.01,.001,1e-4,1e-5,1e-6,1e-7,1e-8,1e-9
```

![12-demo](https://ggmichael.github.io/craterstats/demo/12-demo.png)

Demo 12

```
-title 'Hartmann-style plot with other chronology system,|Poisson age analysis, and without $\mu$-notation'
-pr hartmann
-cs neukumivanov
-mu 0
-ef trask
-p source=%sample%/Pickering.scc,psym=tri,isochron=1,col=red
-p 'type=poisson,range=[.2,.7]'
-p 'colour=red1,psym=filltriangle,range=[2,5],offset=[3,0]'
```

![13-demo](https://ggmichael.github.io/craterstats/demo/13-demo.png)

Demo 13

```
-title Chronology function with Mars epochs and transition times
-pr chronology
-ep mars
-cs neukumivanov
```

![14-demo](https://ggmichael.github.io/craterstats/demo/14-demo.png)

Demo 14

```
-title Chronology function with lunar epochs and transition times
-pr chronology
-ep wilhelms
```

![15-demo](https://ggmichael.github.io/craterstats/demo/15-demo.png)

Demo 15

```
-title 'Impact rate function|with alternative specified reference diameter'
-pr rate
-ref_diameter 10
-yrange -7 2
-ep wilhelms
```

![16-demo](https://ggmichael.github.io/craterstats/demo/16-demo.png)

Demo 16

```
-title 'Poisson calculation for buffered crater count|indicating area and perimeter'
-cs neukum83
-pr diff
-p source=%sample%/c7.scc
-p 'type=b-poisson,range=[.25,2],offset=[-3,2]'
```

![17-demo](https://ggmichael.github.io/craterstats/demo/17-demo.png)

Demo 17

```
-title 'Differential plot|with root-2 binning and root-2 diameter scale'
-cs neukumivanov
-style root-2
-p source=%sample%/Pickering.scc,psym=x,binning=root-2
-p 'type=poisson,range=[.2,.7],isochron=1'
-p 'range=[2,5],colour=violet,offset_age=[2,-3]'
```

![18-demo](https://ggmichael.github.io/craterstats/demo/18-demo.png)

Demo 18

```
-title Cumulative plot with no binning
-pr cumul
-cs neukumivanov
-xrange -2 3
-yrange -5 0
-p source=%sample%/Pickering.scc,binning=none,psym=point
-p 'type=poisson,colour=red,range=[.22,.43],isochron=1'
-p 'range=[2,5],colour=blue,offset=[2,-2]'
```

![19-demo](https://ggmichael.github.io/craterstats/demo/19-demo.png)

Demo 19

```
-title Plot with inverted colour
-cs neukumivanov
-invert 1
-p source=%sample%/Pickering.scc,psym=fo
-p 'type=poisson,range=[.2,.7],isochron=1'
-p 'range=[2,5],colour=violet,offset_age=[2,-3]'
```

![20-demo](https://ggmichael.github.io/craterstats/demo/20-demo.png)

Demo 20

```
-title Plot with left-positioned age annotation
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=fo
-p 'type=poisson,range=[.2,.7]'
-p 'range=[2,5],colour=blue,age_left=1'
```

![21-demo](https://ggmichael.github.io/craterstats/demo/21-demo.png)

Demo 21

```
-title 'Plot with adjusted position of age annotation:|offset_age=[+1,+4] (in 1/20ths of decade)'
-cs neukumivanov
-p source=%sample%/Pickering.scc,psym=fo
-p 'type=poisson,range=[.2,.7]'
-p 'range=[2,5],colour=blue,age_left=1,offset_age=[1,4]'
```

![22-demo](https://ggmichael.github.io/craterstats/demo/22-demo.png)

Demo 22

```
-title Fig 3, Michael et al '(2021)'
-p 'src=%sample%/c1.scc,sym=^,err=0'
-p 'src=%sample%/c2.scc,sym=f^,col=grey'
-p src=%sample%/c3.scc,sym=s4
-p src=%sample%/c4.scc,sym=o
-p src=%sample%/c5.scc,sym=x
-p src=%sample%/c6.scc,sym=s5,col=pink3
-p src=%sample%/c7.scc,sym=sq
-p src=%sample%/Im2.scc,sym=fo,col=blk,err=1
-p 'type=poisson,range=[1.8,20],snap=0,offset=[-5,2]'
-isochrons .5a,.05a,.005s
-xrange -3 2
-yrange -5 5
-pt_size 9
-sf 2
```

<img src = "https://ggmichael.github.io/craterstats/demo/23-demo.svg" width = "100%" />

Demo 23

```
-title Plot in SVG vector format '(PDF' also 'possible)'
-f svg
-p 'src=%sample%/c1.scc,sym=^,err=0'
-p 'src=%sample%/c2.scc,sym=f^,col=grey'
-p src=%sample%/c3.scc,sym=s4
-p src=%sample%/c4.scc,sym=o
-p src=%sample%/c5.scc,sym=x
-p src=%sample%/c6.scc,sym=s5,col=pink3
-p src=%sample%/c7.scc,sym=sq
-p src=%sample%/Im2.scc,sym=fo,col=blk,err=1
-p 'type=poisson,range=[1.8,20],snap=0,offset=[-5,2]'
-isochrons .5a,.05a,.005s
-xrange -3 2
-yrange -5 5
-pt_size 9
-sf 2
```

![24-demo](https://ggmichael.github.io/craterstats/demo/24-demo_err.png)
![24-demo](https://ggmichael.github.io/craterstats/demo/24-demo_k.png)
![24-demo](https://ggmichael.github.io/craterstats/demo/24-demo_age.png)

Demo 24

```
-title 'Evaluation of small-area, low-number count|assuming complete count of craters >150 m'
-pr uncertainty
-cs n83
-ef trask
-d_min 0.15
```

![25-demo](https://ggmichael.github.io/craterstats/demo/25-demo.png)

Demo 25

```
-title 'Bin overlay to aid diameter selection|(normally remove before publication)'
-cs neukumivanov
-p source=%sample%/Pickering.scc,binning=pseudo-log
-p 'type=poisson,range=[.26,.63]'
--bins
```
