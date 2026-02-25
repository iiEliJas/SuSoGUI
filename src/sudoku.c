#include <stdio.h>
#include <string.h>

#define N 9


//
// Sudoku struct - stores the numbers in row, col and box with bits
//      - each number is represented by the index of the set bit
//      - e.g. row[2]=0000001010 -> row 2 contains 1 and 3 
//
typedef struct{
    int row[N];
    int col[N];
    int box[N];
}Sudoku;





//
// Returns index of the lowest set bit (00001100 returns 2)
//
static inline int lowestSetBit(int mask){
    int pos = 0;
    while(pos<10 && !(mask & (1 << pos))) pos++;
    return pos;
}


//
// Returns the number of set bits (00101100 returns 3)
//
static inline int countBits(int mask){
    int count = 0;
    while(mask){
        mask &= (mask-1); // turns of the bit with the lowest index
        count++;
    }
    return count;
}


//
// Returns the index of the box starting at 0 at the top-left and ending at 8 at the bottom-right
//
static inline int getBox(int i, int j) { return(i/3)*3 + (j/3); }


//
// Returns the candidates for a specific cell (i,j) via a bitmask of the digits 
//
static inline int candidates(const Sudoku *s, int i, int j){
    return ~(s->row[i] | s->col[j] | s->box[getBox(i,j)]) & 0x3FE; //0x3FE -> 1111111110 representing all 9 numbers
}


//
// Places the number into the grid and updates the Sudoku bitmasks
//
static inline void placeDigit(Sudoku *s, int grid[N][N], int i, int j, int num){
    grid[i][j] = num;

    s->row[i] |= 1<<num;
    s->col[j] |= 1<<num;
    s->box[getBox(i,j)] |= 1<<num;
}



//
// Removes the number from the grid and updates the Sudoku bitmasks
//
static inline void removeDigit(Sudoku *s, int grid[N][N], int i, int j, int num){
    grid[i][j] = 0;

    s->row[i] &= ~(1<<num);
    s->col[j]  &= ~(1<<num);
    s->box[getBox(i,j)] &= ~(1<<num);
 
}


//
// Initializes the sudoku
//
static int initSudoku(Sudoku *s, int grid[N][N]){
    memset(s, 0, sizeof(Sudoku));

    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            if(grid[i][j]){
                int bit = 1 << grid[i][j];
                if(s->row[i] & bit || s->col[j] & bit || s->box[getBox(i,j)] & bit) return 0;
                placeDigit(s, grid, i,j, grid[i][j]);
            }
        }
    }
    return 1;
}


//
// Finds the best empty cell - the cell with the fewest candidates
// Returns 1 if found and 0 if the board is full
//
static int findBestCell(int grid[N][N], const Sudoku *s, int *bi, int *bj){
    int best = 10;

    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            if(grid[i][j] != 0) continue;

            int mask = candidates(s, i,j);
            int count = countBits(mask);

            if(count==0) return -1;     // -> contradiction
            if(count<best){
                best = count;
                *bi = i;
                *bj = j;
                if (best<=1) return 1;
            }
        }
    }

    return best<10;
}



//
// Fills all empty cells with only one candidate
// Stores all placed cells in fi and fj for backtracking
// Returns 0 on contradiction and 1 otherwise
//
static int fillSingles(int grid[N][N], Sudoku *s, int *fi, int *fj, int *count){
    int finished=0;
    while(!finished){
        finished = 1;

        for(int i=0; i<N; i++){
            for(int j=0; j<N; j++){
                if(grid[i][j]!=0) continue;

                int mask = candidates(s,i,j);
                if(mask==0) return 0;           // -> contradiction

                if((mask & (mask-1)) == 0) {      // one bit is set
                    int num = lowestSetBit(mask);
                    placeDigit(s, grid, i,j, num);

                    fi[*count] = i;
                    fj[*count] = j;
                    (*count)++;
                    finished = 0;
                }

            }
        }
    }
    return 1;
}


//
// Backtracking solver
//
static int solveInternal(int grid[N][N], Sudoku *s, int *fi, int *fj, int depth){
    int filled = 0;

    if(fillSingles(grid, s, fi+depth, fj+depth, &filled)){
        int bi, bj;
        int res = findBestCell(grid, s, &bi, &bj);
        if(res==0) return 1;   // no empty cells left
        
        if(res!=-1){   // res==-1 -> contradiction
            int mask = candidates(s,bi,bj);
            if(mask!=0){
                // Try each mask digit
                while(mask){
                    int num = lowestSetBit(mask);
                    mask &= mask-1;

                    placeDigit(s, grid, bi,bj, num);
                    if(solveInternal(grid,s, fi,fj, depth+filled)) return 1;
                    removeDigit(s,grid,bi,bj,num);
                }
            }
        }
    }

    // Undo the filled single cells
    for(int k=filled-1; k>=0; k--){     
        int i = depth+k;
        int num = grid[fi[i]][fj[i]];
        removeDigit(s, grid, fi[i], fj[i], num);
    }
    return 0;
}




int solveSudoku(int arr[N*N]){
    int grid[N][N];
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            grid[i][j] = arr[N*i + j];
        }
    }

    Sudoku s;
    if(!initSudoku(&s, grid)) return 0;     // not solvable

    int fi[N*N], fj[N*N];
    if(!solveInternal(grid, &s, fi,fj, 0)) return 0;  // not solvable

    
    // Result back into the array
    for(int i=0; i<N; i++){
        for(int j=0; j<N; j++){
            arr[N*i + j] = grid[i][j];
        }
    }
    
    return 1;
}








