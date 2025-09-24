#ifndef LOW_PASS_FILTER_H
#define LOW_PASS_FILTER_H

class LowPassFilter {
public:
    LowPassFilter(float cutoffFreq, float sampleRate);
    void setAlpha(float cutoffFreq, float sampleRate);
    float update(float input);

    void setInitial(float value);  // ← Establece el valor de salida manualmente
    void clear();                  // ← Borra el estado interno, próxima entrada pasa directo

private:
    float alpha;
    float prevOutput;
    bool initialized = false;
};

#endif
