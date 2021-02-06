#pragma once

#define IS_DEBUG true
#define VERBOSE 3 // how much debugging info to output. Range between 0 and 3
#define getVarName(a) #a

// void debug(const std::string &message, int line = -1);
// void debug(int line = -1);
// void debugVar(const std::string &varName, int var);
// void debugVar(const std::string &varName, std::pair<int, int> var);
// void debugVar(int var);
// void debugVar(std::pair<int, int> var);

// template <typename T>
// void func(T t)
// {
//     std::cout << t << std::endl ;
// }

template<typename T, typename... Args>
void func(T t, Args... args){
  std::cout << t << std::endl;
  func(args...);
}



int debugNum = 0;

void debug(const std::string &message, int line){
    // message.replace(0, 1, toupper(message.at(0)));
    if (not IS_DEBUG)
        return;

    if (line >= 0)
        std::cout << ++debugNum << ": " << message << " @ line " << line << std::endl;
    else
        std::cout << ++debugNum << ": " << message << std::endl;
}

void debug(int line){
    if (not IS_DEBUG)
        return;

    if (line >= 0)
        std::cout << ++debugNum << ": Line " << line << std::endl;
    else
        std::cout << ++debugNum << std::endl;
}

void debugVar(const std::string &varName, int var){
    if (not IS_DEBUG)
        return;

    std::cout << ++debugNum << ": " << varName << " = " << var << std::endl;
}

void debugVar(const std::string &varName, std::pair<int, int> var){
    if (not IS_DEBUG)
        return;

    std::cout << ++debugNum << ": " << varName << " = (" << var.first << ", " << var.second << ")\n";
}

void debugVar(int var){
    if (not IS_DEBUG)
        return;

    std::cout << ++debugNum << ": "  << var << std::endl;
}

void debugVar(std::pair<int, int> var){
    if (not IS_DEBUG)
        return;

    std::cout << ++debugNum << ": " << "(" << var.first << ", " << var.second << ")\n";
}