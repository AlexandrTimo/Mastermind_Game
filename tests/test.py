'''
🔬 Test cases you should add (table-driven)
secret
guess
           CN       CL
0 1 3 5     
2 2 4 6     0       0

0 1 3 5
0 2 4 6     1       1
                    
0 1 3 5
2 2 1 1     1       0
    
0 1 3 5
0 1 5 6     3       2
        
1 1 2 3
1 2 1 1     3       1
            
7 7 7 7
7 0 7 0     2       2
            
0 0 1 1
1 1 0 0     4       0
            
0 2 2 3
2 2 2 2     3       2
            
3 4 5 6
3 4 5 6     4       4
            

Also add negative tests:
Length ≠ 4, values outside 0..7, non-ints → should raise.

'''