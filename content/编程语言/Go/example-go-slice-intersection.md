---
id: example-go-slice-intersection
type: 手撕代码
difficulty: easy
tags: [Go, 切片, map, 交集]
sources: [example]
date: 2026-11-13
---

## 题目
用 Go 实现两个切片（slice）的交集，要求结果元素不重复。

## 回答
用一个 map 对第一个切片去重，再遍历第二个切片判断是否命中：

```go
func intersect(a, b []int) []int {
    seen := make(map[int]bool, len(a))
    for _, v := range a {
        seen[v] = true
    }
    var out []int
    for _, v := range b {
        if seen[v] {
            out = append(out, v)
            delete(seen, v) // 命中后删除，保证结果不重复
        }
    }
    return out
}
```

时间复杂度 O(n+m)，空间复杂度 O(n)。
