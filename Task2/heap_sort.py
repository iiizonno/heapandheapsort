from heap import Heap

def heap_sort(arr: list[int]) -> None:
    if len(arr) <= 1:
        return
    heap = Heap(arr)
    for i in range(len(arr) - 1, -1, -1):
        arr[i] = heap.extract_min()
    arr.reverse()
