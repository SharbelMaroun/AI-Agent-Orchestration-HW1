# RNN Architecture & Implementation

## 1. The Mathematical Foundation
To code an RNN, you must implement the core recursive formula. In each time step ($t$), the network combines the current input ($x_t$) with the memory of the previous step ($h_{t-1}$). The standard formula used in libraries like PyTorch and TensorFlow is the Concatenated Form:
$$h_{t} = \sigma(W \cdot [x_{t}, h_{t-1}] + b)$$
- **$x_t$:** Current input (e.g., today's stock price).
- **$h_{t-1}$:** Previous hidden state (memory from yesterday).
- **$W$:** Shared weights (used for every time step).
- **$b$:** Bias.
- **$\sigma$:** Activation function, typically Tanh.

## 2. Implementing the RNN Architecture
The implementation follows the "Unrolling" concept, where we process the sequence step-by-step.

### Step A: Tokenization and Embedding
Before feeding data into the RNN, you must perform Tokenization (splitting data into units like words or days) and Embedding (converting units into numerical vectors).

### Step B: The Forward Pass (Python Logic)
You can implement the forward pass using a simple loop that "unrolls" the network over time:
- **Initialize the Hidden State:** Start with a vector of zeros ($h_0$).
- **Loop through the Sequence:** For every element in your input sequence:
  - Calculate the weighted sum of the input and the previous hidden state.
  - Apply the activation function (Tanh) to get the new hidden state ($h_t$).
  - Store $h_t$ to be used as the input for the next step.

## 3. Key Implementation Principles
To ensure the RNN works correctly according to Dr. Segal's analysis, you must respect these rules:
- **Weight Sharing:** Do not create new weights for each step. Use the same $W$ and $b$ matrices throughout the entire loop. This keeps the parameter count constant and memory usage efficient.
- **Sequential Order:** Data must be fed from oldest to newest. Reversing the order will break the temporal logic the RNN is trying to learn.
- **Activation Choice:** Use Tanh for hidden layers as it is zero-centered and keeps gradients more stable than Sigmoid.

## 4. Handling Training Challenges
When you move to the training phase (Backpropagation Through Time), you will encounter the Gradient Problem:
- **Vanishing Gradients:** If weights are small ($<1$), the gradient shrinks to zero over long sequences, and the network "forgets" early inputs.
- **Exploding Gradients:** If weights are large ($>1$), the gradient grows exponentially, causing numerical instability (NaN values).

**The Solution:** For real-world Python implementation, it is often better to use LSTM (Long Short-Term Memory) layers. LSTMs use "Gates" (Forget, Input, and Output gates) to create a "highway" for information, preventing the gradient from disappearing over long sequences.

## Summary Table for Implementation
| Component | Implementation Detail |
| :--- | :--- |
| **Input Shape** | (Batch Size, Sequence Length, Input Features) |
| **Hidden State** | Initialize as zeros; update at each step |
| **Weights** | Shared across all time steps |
| **Activation** | tanh for hidden, MSE or Cross-Entropy for loss |
