int n     = ...;   // liczba kartonow
int Kmax  = ...;   // liczba dostepnych ciezarowek (gorne ograniczenie)

range I   = 1..n;     // kartony
range K   = 1..Kmax;  // ciezarowki
range Dim = 1..3;     // 1 = X (szerokosc), 2 = Y (wysokosc), 3 = Z (glebokosc)
range O   = 1..6;     // 6 orientacji osiowych
range S   = 1..6;     // 6 binarnych zmiennych rozdzielajacych dla pary

float boxDim[I][Dim] = ...;
float weight[I]      = ...;   // waga kartonu

float W = ...;   // szerokosc naczepy (os X)
float H = ...;   // wysokosc naczepy  (os Y)
float D = ...;   // glebokosc naczepy (os Z)
float Q = ...;   // ladownosc (limit wagi)

tuple Pair { int i; int j; }
{Pair} Deps = ...;

{Pair} Pairs = { <i,j> | i,j in I : i < j };

int perm[O][Dim] = [ [1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1] ];

dvar boolean y[K];        // ciezarowka k jest uzyta
dvar boolean x[I][K];     // karton i jedzie ciezarowka k
dvar boolean ori[I][O];   // wybrana orientacja kartonu i
dvar float+  px[I];       // wspolrzedne lewego-dolnego-tylnego naroza
dvar float+  py[I];
dvar float+  pz[I];
dvar boolean sep[Pairs][S]; // rozdzielenie pary i<j wzdluz osi (big-M)

dexpr float lx[i in I] = sum(o in O) boxDim[i][perm[o][1]] * ori[i][o];
dexpr float ly[i in I] = sum(o in O) boxDim[i][perm[o][2]] * ori[i][o];
dexpr float lz[i in I] = sum(o in O) boxDim[i][perm[o][3]] * ori[i][o];

minimize sum(k in K) y[k];

subject to {
  // (1) kazdy karton dokladnie raz
  forall(i in I)
    assignOnce: sum(k in K) x[i][k] == 1;

  // (2) kazdy karton ma dokladnie jedna orientacje
  forall(i in I)
    oneOrientation: sum(o in O) ori[i][o] == 1;

  // (3) kartony trafiaja tylko do uzytych ciezarowek
  forall(i in I, k in K)
    onlyIfUsed: x[i][k] <= y[k];

  // (4) limit wagi w ciezarowce
  forall(k in K)
    weightCap: sum(i in I) weight[i] * x[i][k] <= Q * y[k];

  // (5) zaleznosci: jesli i jest w k, to j tez musi byc w k
  forall(p in Deps, k in K)
    dependency: x[p.i][k] <= x[p.j][k];

  // (6) karton miesci sie w wymiarach naczepy
  forall(i in I) {
    fitX: px[i] + lx[i] <= W;
    fitY: py[i] + ly[i] <= H;
    fitZ: pz[i] + lz[i] <= D;
  }

  // (7) brak nakladania sie kartonow w tej samej ciezarowce
  forall(p in Pairs) {
    sepXleft:   px[p.i] + lx[p.i] <= px[p.j] + W * (1 - sep[p][1]);
    sepXright:  px[p.j] + lx[p.j] <= px[p.i] + W * (1 - sep[p][2]);
    sepYbelow:  py[p.i] + ly[p.i] <= py[p.j] + H * (1 - sep[p][3]);
    sepYabove:  py[p.j] + ly[p.j] <= py[p.i] + H * (1 - sep[p][4]);
    sepZback:   pz[p.i] + lz[p.i] <= pz[p.j] + D * (1 - sep[p][5]);
    sepZfront:  pz[p.j] + lz[p.j] <= pz[p.i] + D * (1 - sep[p][6]);

    // rozdzielenie wymuszane tylko gdy oba w tej samej ciezarowce
    forall(k in K)
      noOverlap: sum(t in S) sep[p][t] >= x[p.i][k] + x[p.j][k] - 1;
  }

  // (8) lamanie symetrii: ciezarowki zapelniane po kolei
  forall(k in K : k < Kmax)
    symmetry: y[k] >= y[k+1];
}

execute DISPLAY {
  var used = 0;
  for (var kk in K) used += y[kk];
  writeln("Uzytych ciezarowek: ", used);
  for (var k in K) if (y[k] == 1) {
    writeln("Ciezarowka ", k, ":");
    for (var i in I) if (x[i][k] == 1)
      writeln("  karton ", i,
              "  poz=(", px[i], ",", py[i], ",", pz[i], ")",
              "  wym=(", lx[i], ",", ly[i], ",", lz[i], ")");
  }
}
