#ifndef PATHS_H
#define PATHS_H

#define N_PATHS  14

// 1. Number of points per path
extern const int path_sizes[N_PATHS];

// 2. Individual path data
extern const float path0_x[];
extern const float path0_y[];

extern const float path1_x[];
extern const float path1_y[];

extern const float path2_x[];
extern const float path2_y[];

extern const float path3_x[];
extern const float path3_y[];

extern const float path4_x[];
extern const float path4_y[];

extern const float path5_x[];
extern const float path5_y[];

extern const float path6_x[];
extern const float path6_y[];

extern const float path7_x[];
extern const float path7_y[];

extern const float path8_x[];
extern const float path8_y[];

extern const float path9_x[];
extern const float path9_y[];

extern const float path10_x[];
extern const float path10_y[];

extern const float path11_x[];
extern const float path11_y[];

extern const float path12_x[];
extern const float path12_y[];

extern const float path13_x[];
extern const float path13_y[];

// 3. Arrays of pointers to select active path
extern const float* path_x[N_PATHS];
extern const float* path_y[N_PATHS];

#endif
