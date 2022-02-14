#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

data_source = './scenario_test.csv'
df = pd.read_csv(data_source, header=None)

plt.figure()
plt.plot(df[1], df[0])
plt.xticks([1, 2, 4, 8])
plt.xlabel('Concurrency')
plt.ylabel('Throughput (MB/s)')
plt.title('Concurrency vs. Throughput')
plt.savefig('./analysis.pdf', figsize=(4,7))
plt.show()
