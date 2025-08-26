  
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
