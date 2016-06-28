      SUBROUTINE   N2GB(N, P, X, B, CALCR, CALCJ, IV, LIV, LV, V,
     1                  UIPARM, URPARM, UFPARM)
C
C  ***  VERSION OF NL2SOL THAT HANDLES SIMPLE BOUNDS ON X  ***
C
C  ***  PARAMETERS  ***
C
      INTEGER N, P, LIV, LV
C/6
C     INTEGER IV(LIV), UIPARM(1)
C     REAL X(P), B(2,P), V(LV), URPARM(1)
C/7
      INTEGER IV(LIV), UIPARM(*)
      REAL X(P), B(2,P), V(LV), URPARM(*)
C/
      EXTERNAL CALCR, CALCJ, UFPARM
C
C  ***  DISCUSSION  ***
C
C        NOTE... NL2SOL (MENTIONED BELOW) IS A CODE FOR SOLVING
C     NONLINEAR LEAST-SQUARES PROBLEMS.  IT IS DESCRIBED IN
C     ACM TRANS. MATH. SOFTWARE, VOL. 7 (1981), PP. 369-383
C     (AN ADAPTIVE NONLINEAR LEAST-SQUARES ALGORITHM, BY J.E. DENNIS,
C     D.M. GAY, AND R.E. WELSCH).
C
C        LIV GIVES THE LENGTH OF IV.  IT MUST BE AT LEAST 82 + 4*P.
C     IF NOT, THEN   N2GB RETURNS WITH IV(1) = 15.  WHEN   N2GB
C     RETURNS, THE MINIMUM ACCEPTABLE VALUE OF LIV IS STORED IN
C     IV(LASTIV) = IV(44), (PROVIDED THAT LIV .GE. 44).
C
C        LV GIVES THE LENGTH OF V.  THE MINIMUM VALUE FOR LV IS
C     LV0 = 105 + P*(N + 2*P + 21) + 2*N.  IF LV IS SMALLER THAN THIS,
C     THEN   N2GB RETURNS WITH IV(1) = 16.  WHEN   N2GB RETURNS, THE
C     MINIMUM ACCEPTABLE VALUE OF LV IS STORED IN IV(LASTV) = IV(45)
C     (PROVIDED LIV .GE. 45).
C
C        RETURN CODES AND CONVERGENCE TOLERANCES ARE THE SAME AS FOR
C     NL2SOL, WITH SOME SMALL EXTENSIONS... IV(1) = 15 MEANS LIV WAS
C     TOO SMALL.   IV(1) = 16 MEANS LV WAS TOO SMALL.
C
C        THERE ARE TWO NEW V INPUT COMPONENTS...  V(LMAXS) = V(36) AND
C     V(SCTOL) = V(37) SERVE WHERE V(LMAX0) AND V(RFCTOL) FORMERLY DID
C     IN THE SINGULAR CONVERGENCE TEST -- SEE THE NL2SOL DOCUMENTATION.
C
C  ***  BOUNDS  ***
C
C     THE BOUNDS  B(1,I) .LE. X(I) .LE. B(2,I), I = 1(1)P, ARE ENFORCED.
C
C  ***  DEFAULT VALUES  ***
C
C        DEFAULT VALUES ARE PROVIDED BY SUBROUTINE IVSET, RATHER THAN
C     DFAULT.  THE CALLING SEQUENCE IS...
C             CALL IVSET(1, IV, LIV, LV, V)
C     THE FIRST PARAMETER IS AN INTEGER 1.  IF LIV AND LV ARE LARGE
C     ENOUGH FOR IVSET, THEN IVSET SETS IV(1) TO 12.  OTHERWISE IT
C     SETS IV(1) TO 15 OR 16.  CALLING   N2GB WITH IV(1) = 0 CAUSES ALL
C     DEFAULT VALUES TO BE USED FOR THE INPUT COMPONENTS OF IV AND V.
C        IF YOU FIRST CALL IVSET, THEN SET IV(1) TO 13 AND CALL   N2GB,
C     THEN STORAGE ALLOCATION ONLY WILL BE PERFORMED.  IN PARTICULAR,
C     IV(D) = IV(27), IV(J) = IV(70), AND IV(R) = IV(61) WILL BE SET
C     TO THE FIRST SUBSCRIPT IN V OF THE SCALE VECTOR, THE JACOBIAN
C     MATRIX, AND THE RESIDUAL VECTOR RESPECTIVELY, PROVIDED LIV AND LV
C     ARE LARGE ENOUGH.  IF SO, THEN   N2GB RETURNS WITH IV(1) = 14.
C     WHEN CALLED WITH IV(1) = 14,   N2GB ASSUMES THAT STORAGE HAS
C     BEEN ALLOCATED, AND IT BEGINS THE MINIMIZATION ALGORITHM.
C
C  ***  SCALE VECTOR  ***
C
C        ONE DIFFERENCE WITH NL2SOL IS THAT THE SCALE VECTOR D IS
C     STORED IN V, STARTING AT A DIFFERENT SUBSCRIPT.  THE STARTING
C     SUBSCRIPT VALUE IS STILL STORED IN IV(D) = IV(27).  THE
C     DISCUSSION OF DEFAULT VALUES ABOVE TELLS HOW TO HAVE IV(D) SET
C     BEFORE THE ALGORITHM IS STARTED.
C
C  ***  GENERAL  ***
C
C     CODED BY DAVID M. GAY.
C
C  ***  EXTERNAL SUBROUTINES  ***
C
      EXTERNAL IVSET,  RN2GB
C IVSET.... PROVIDES DEFAULT IV AND V INPUT COMPONENTS.
C  RN2GB... CARRIES OUT OPTIMIZATION ITERATIONS.
C
C  ***  LOCAL VARIABLES  ***
C
      INTEGER D1, DR1, IV1, N1, N2, NF, R1, RD1
C
C  ***  IV COMPONENTS  ***
C
      INTEGER D, J, NEXTV, NFCALL, NFGCAL, R, REGD0, TOOBIG, VNEED
C/6
C     DATA D/27/, J/70/, NEXTV/47/, NFCALL/6/, NFGCAL/7/, R/61/,
C    1     REGD0/82/, TOOBIG/2/, VNEED/4/
C/7
      PARAMETER (D=27, J=70, NEXTV=47, NFCALL=6, NFGCAL=7, R=61,
     1           REGD0=82, TOOBIG=2, VNEED=4)
C/
C---------------------------------  BODY  ------------------------------
C
      IF (IV(1) .EQ. 0) CALL IVSET(1, IV, LIV, LV, V)
      IV1 = IV(1)
      IF (IV1 .EQ. 14) GO TO 10
      IF (IV1 .GT. 2 .AND. IV1 .LT. 12) GO TO 10
      IF (IV1 .EQ. 12) IV(1) = 13
      IF (IV(1) .EQ. 13) IV(VNEED) = IV(VNEED) + P + N*(P+2)
      CALL  RN2GB(B, X, V, IV, LIV, LV, N, N, N1, N2, P, V, V, V, X)
      IF (IV(1) .NE. 14) GO TO 999
C
C  ***  STORAGE ALLOCATION  ***
C
      IV(D) = IV(NEXTV)
      IV(R) = IV(D) + P
      IV(REGD0) = IV(R) + N
      IV(J) = IV(REGD0) + N
      IV(NEXTV) = IV(J) + N*P
      IF (IV1 .EQ. 13) GO TO 999
C
 10   D1 = IV(D)
      DR1 = IV(J)
      R1 = IV(R)
      RD1 = IV(REGD0)
C
 20   CALL  RN2GB(B, V(D1), V(DR1), IV, LIV, LV, N, N, N1, N2, P, V(R1),
     1            V(RD1), V, X)
      IF (IV(1)-2) 30, 50, 999
C
C  ***  NEW FUNCTION VALUE (R VALUE) NEEDED  ***
C
 30   NF = IV(NFCALL)
      CALL CALCR(N, P, X, NF, V(R1), UIPARM, URPARM, UFPARM)
      IF (NF .GT. 0) GO TO 40
         IV(TOOBIG) = 1
         GO TO 20
 40   IF (IV(1) .GT. 0) GO TO 20
C
C  ***  COMPUTE DR = GRADIENT OF R COMPONENTS  ***
C
 50   CALL CALCJ(N, P, X, IV(NFGCAL), V(DR1), UIPARM, URPARM, UFPARM)
      IF (IV(NFGCAL) .EQ. 0) IV(TOOBIG) = 1
      GO TO 20
C
 999  RETURN
C
C  ***  LAST CARD OF   N2GB FOLLOWS  ***
      END
