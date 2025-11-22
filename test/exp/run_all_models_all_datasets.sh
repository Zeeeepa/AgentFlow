#!/bin/bash
# Usage: bash exp/run_all_models_all_datasets.sh
# Model format: "port:modelname,label,enabled_tools,tool_engines,model_engines"
# Example: "8000:vllm-IPF/model1,label1,Tool1|Tool2,engine1|engine2,trainable|dashscope|dashscope|dashscope"
# - port: VLLM server port (leave empty for API-based models)
# - modelname: Model name (e.g., vllm-AgentFlow/agentflow-planner-7b)
# - label: Human-readable label for results
# - enabled_tools: Tools to enable (| separated)
# - tool_engines: Engine for each tool (| separated)
# - model_engines: [planner_main|planner_fixed|verifier|executor] - use "trainable" for components using the main model

############ Configuration ############
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Set project directory to test/ folder (parent of exp/)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
THREADS=20

# Define all tasks to run
TASKS=(
    # "gameof24"
    "aime24"
    # "amc23"
    # "bamboogle"
    # "2wiki"
    # "gaia"
    # "musique"
    # "hotpotqa"
    # "medqa"
    # "gpqa"
)

# Define models with their tool configurations in format:
# "port:modelname,label,enabled_tools,tool_engines,model_engines"
# - enabled_tools: use | as separator (will be converted to comma)
# - tool_engines: use | as separator (will be converted to comma)
# - model_engines: use | as separator (will be converted to comma) - [planner_main|planner_fixed|verifier|executor]
# - If port is empty (e.g., ":modelname"), base_url will not be passed to solver
# Example with trainable planner: "8000:vllm-IPF/model,label,Tool1|Tool2,engine1|Default,trainable|dashscope|dashscope|dashscope"
# Example all fixed: ":dashscope,Dashscope,Tool1|Tool2,Default|Default,dashscope|dashscope|dashscope|dashscope"
MODELS=(
    "8000:vllm-AgentFlow/agentflow-planner-7b,AgentFlow-7B,\
Base_Generator_Tool|Python_Coder_Tool|Google_Search_Tool|Wikipedia_Search_Tool,\
gpt-4o-mini|dashscope-qwen2.5-7b-coder-instruct|Default|Default,\
trainable|dashscope|dashscope|dashscope"
#     ":dashscope-qwen2.5-7b-instruct,Qwen2.5-7b-naive,\
# Base_Generator_Tool|Python_Coder_Tool|Google_Search_Tool|Wikipedia_Search_Tool,\
# dashscope-qwen2.5-7b-instruct|dashscope-qwen2.5-7b-instruct|Default|Default,\
# trainable|dashscope|dashscope|dashscope"
)

DATA_FILE_NAME="data.json"

############################################

cd $PROJECT_DIR

# Loop through all models
for MODEL_SPEC in "${MODELS[@]}"; do
    # Parse model specification: port:modelname,label,enabled_tools,tool_engines,model_engines
    PORT=$(echo "$MODEL_SPEC" | cut -d':' -f1)
    REST=$(echo "$MODEL_SPEC" | cut -d':' -f2-)

    # Split by comma to get individual fields
    IFS=',' read -r LLM LABEL ENABLED_TOOLS_RAW TOOL_ENGINE_RAW MODEL_ENGINE_RAW <<< "$REST"

    # Convert | separators to commas for configuration
    ENABLED_TOOLS=$(echo "$ENABLED_TOOLS_RAW" | tr '|' ',')
    TOOL_ENGINE=$(echo "$TOOL_ENGINE_RAW" | tr '|' ',')
    MODEL_ENGINE=$(echo "$MODEL_ENGINE_RAW" | tr '|' ',')

    # If MODEL_ENGINE is empty, use default
    if [ -z "$MODEL_ENGINE" ]; then
        MODEL_ENGINE="trainable,dashscope,dashscope,dashscope"
    fi

    # Set BASE_URL only if PORT is not empty
    if [ -n "$PORT" ]; then
        BASE_URL="http://localhost:${PORT}/v1"
        USE_BASE_URL=true
    else
        BASE_URL=""
        USE_BASE_URL=false
    fi

    echo "========================================"
    echo "MODEL: $LLM"
    echo "LABEL: $LABEL"
    if [ "$USE_BASE_URL" = true ]; then
        echo "BASE_URL: $BASE_URL"
    else
        echo "BASE_URL: Not used (using default API endpoint)"
    fi
    echo "ENABLED_TOOLS: $ENABLED_TOOLS"
    echo "TOOL_ENGINE: $TOOL_ENGINE"
    echo "MODEL_ENGINE: $MODEL_ENGINE"
    echo "========================================"

    # Loop through all tasks
    for TASK in "${TASKS[@]}"; do
        echo "============================="
        echo "Starting task: $TASK with model: $LABEL"
        echo "============================="

        DATA_FILE="$TASK/data/$DATA_FILE_NAME"
        LOG_DIR="$TASK/logs/$LABEL"
        OUT_DIR="$TASK/results/$LABEL"
        CACHE_DIR="$TASK/cache"

        mkdir -p "$LOG_DIR"
        mkdir -p "$OUT_DIR"

        # Define indices based on task
        case $TASK in
            bamboogle)
                indices=($(seq 0 124))   # 0~124
                ;;
            gaia)
                indices=($(seq 0 126))   # 0~126
                ;;
            aime24)
                indices=($(seq 0 29))
                ;;
            2wiki|gameof24|amc23|nq|musique|hotpotqa|popqa|medqa|gpqa)
                indices=($(seq 0 99))
                ;;
            *)
                indices=(0)  # dafault
                ;;
        esac

        # Skip already completed indices
        new_indices=()
        for i in "${indices[@]}"; do
            if [ ! -f "$OUT_DIR/output_$i.json" ]; then
                new_indices+=($i)
            else
                echo "Output file already exists: $OUT_DIR/output_$i.json"
            fi
        done
        indices=("${new_indices[@]}")
        echo "Final indices: ${indices[@]}"

        if [ ${#indices[@]} -eq 0 ]; then
            echo "All subtasks completed for $TASK with $LABEL."
        else
            # Define single task function
            echo "Using model: $LLM"
            run_task() {
                local i=$1
                echo "Running $TASK for index $i"

                # Build command with conditional base_url parameter
                if [ "$USE_BASE_URL" = true ]; then
                    uv run python solve.py \
                    --index $i \
                    --task $TASK \
                    --data_file $DATA_FILE \
                    --llm_engine_name $LLM \
                    --root_cache_dir $CACHE_DIR \
                    --output_json_dir $OUT_DIR \
                    --output_types direct \
                    --enabled_tools "$ENABLED_TOOLS" \
                    --tool_engine "$TOOL_ENGINE" \
                    --model_engine "$MODEL_ENGINE" \
                    --max_time 300 \
                    --max_steps 10 \
                    --temperature 0.7 \
                    --base_url "$BASE_URL" \
                    2>&1 | tee "$LOG_DIR/$i.log"
                else
                    uv run python solve.py \
                    --index $i \
                    --task $TASK \
                    --data_file $DATA_FILE \
                    --llm_engine_name $LLM \
                    --root_cache_dir $CACHE_DIR \
                    --output_json_dir $OUT_DIR \
                    --output_types direct \
                    --enabled_tools "$ENABLED_TOOLS" \
                    --tool_engine "$TOOL_ENGINE" \
                    --model_engine "$MODEL_ENGINE" \
                    --max_time 300 \
                    --max_steps 10 \
                    --temperature 0.7 \
                    2>&1 | tee "$LOG_DIR/$i.log"
                fi

                echo "Completed $TASK for index $i"
                echo "------------------------"
            }
            export -f run_task
            export TASK DATA_FILE LOG_DIR OUT_DIR CACHE_DIR LLM ENABLED_TOOLS TOOL_ENGINE MODEL_ENGINE BASE_URL USE_BASE_URL

            echo "Starting parallel execution for $TASK..."
            parallel -j $THREADS run_task ::: "${indices[@]}"
            echo "All subtasks completed for $TASK with $LABEL."
        fi

        ############ Calculate Scores ############
        RESPONSE_TYPE="direct_output"
        uv run python calculate_score_unified.py \
        --task_name $TASK \
        --data_file $DATA_FILE \
        --result_dir $OUT_DIR \
        --response_type $RESPONSE_TYPE \
        --output_file "finalresults_$RESPONSE_TYPE.json" \
        | tee "$OUT_DIR/finalscore_$RESPONSE_TYPE.log"

    done

    echo "========================================"
    echo "Completed all tasks for model: $LABEL"
    echo "========================================"
done

echo "============================="
echo "All models and tasks finished!"
echo "============================="